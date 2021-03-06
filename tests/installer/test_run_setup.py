# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013, Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import shutil
import sys
from unittest import TestCase

from packstack.modules import ospluginutils
from packstack.installer import run_setup, basedefs

from ..test_base import PackstackTestCaseMixin


class CommandLineTestCase(PackstackTestCaseMixin, TestCase):
    def test_running_install_hosts(self):
        """
        Test packstack.installer.run_setup.main

        This test effectivly runs all of the python code ran by
        packstack --install-hosts=127.0.0.1 --os-swift-install=y \
        --nagios-install=y

        It is a fairly wide net but boost code coverage of the packstack
        python code to about 85%, more finer grained tests should also be
        Added to target speficic test cases.

        Popen is replaced in PackstackTestCaseMixin so no actual commands get
        run on the host running the unit tests
        """

        # create a dummy public key
        dummy_public_key = os.path.join(self.tempdir, 'id_rsa.pub')
        open(dummy_public_key, 'w').close()

        # Save sys.argv and replace it with the args we want optparse to use
        orig_argv = sys.argv
        sys.argv = ['packstack', '--ssh-public-key=%s' % dummy_public_key,
                    '--install-hosts=127.0.0.1', '--os-swift-install=y',
                    '--nagios-install=y']

        # There is no puppet logfile to validate, so replace
        # ospluginutils.validate_puppet_logfile with a mock function
        orig_validate_logfile = ospluginutils.validate_puppet_logfile
        ospluginutils.validate_puppet_logfile = lambda a: None

        # If there is a error in a plugin sys.exit() gets called, this masks
        # the actual error that should be reported, so we replace it to
        # raise Exception, packstack logging gives a more infomrative error
        def raise_(ex):
            raise ex
        orig_sys_exit = sys.exit
        sys.exit = lambda a: raise_(Exception('Error during install-hosts'))

        try:
            run_setup.main()
        finally:
            sys.argv = orig_argv
            ospluginutils.validate_puppet_logfile = orig_validate_logfile
            sys.exit = orig_sys_exit
            try:
                shutil.rmtree(basedefs.VAR_DIR)
            except:
                pass
