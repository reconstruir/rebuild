#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os, os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.file_find import file_find
from bes.fs.temp_file import temp_file
from bes.system.os_env import os_env
from rebuild.native_package.native_package import native_package
from bes.testing.unit_test_skip import skip_if
from bes.system.host import host

class test_jail_cli(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/jail_cli'

  DEBUG = False
  #DEBUG = True

  __BES_JAIL_PY = path.normpath(path.join(path.dirname(__file__), '../../../../bin/rebuild_jail.py'))

#com.apple.pkg.JavaTools
#com.apple.pkg.MobileDevice
#com.apple.pkg.MobileDeviceDevelopment

  _PACKAGE_ID = 'com.apple.pkg.MobileDevice'

  @skip_if(not host.is_macos(), 'not macos')
  @skip_if(not native_package().is_installed(_PACKAGE_ID), 'not installed: %s' % (_PACKAGE_ID))
  def test_create_from_packages(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    jail_config_content = '''
[jail]
description: test
packages:
  %s
[%s]
''' % (self._PACKAGE_ID, self._PACKAGE_ID)
    tmp_jail_config = temp_file.make_temp_file(content = jail_config_content)
    cmd = [
      self.__BES_JAIL_PY,
      'create',
      tmp_dir,
      tmp_jail_config,
    ]
    rv = os_env.call_python_script(cmd)
    print(rv.stdout)
    self.assertEqual( 0, rv.exit_code )

    expected_files = npm.package_contents(self._PACKAGE_ID)
    actual_files = file_find.find(tmp_dir, file_type = file_find.ANY, relative = True)
    actual_files = [ path.join('/', f) for f in actual_files ]
    self.assertEqual( expected_files, actual_files )

  @skip_if(not host.is_macos(), 'not macos')
  def test_create_from_binaries(self):
    self.maxDiff = None
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    jail_config_content = '''
[jail]
description: test
binaries:
  /bin/bash
  /bin/echo
  /bin/ls
  /bin/sh
  /usr/lib/dyl*
'''
    tmp_jail_config = temp_file.make_temp_file(content = jail_config_content)
    cmd = [
      self.__BES_JAIL_PY,
      'create',
      tmp_dir,
      tmp_jail_config,
    ]
    rv = os_env.call_python_script(cmd)
    print(rv.stdout)
    self.assertEqual( 0, rv.exit_code )

    expected_files = sorted([
      '/bin',
      '/bin/bash',
      '/bin/echo',
      '/bin/ls',
      '/bin/sh',
      '/usr',
      '/usr/lib',
      '/usr/lib/dyld',
      '/usr/lib/dylib1.10.5.o',
      '/usr/lib/dylib1.o',
      '/usr/lib/libDiagnosticMessagesClient.dylib',
      '/usr/lib/libSystem.B.dylib',
      '/usr/lib/libauto.dylib',
      '/usr/lib/libc++.1.dylib',
      '/usr/lib/libc++abi.dylib',
      '/usr/lib/libncurses.5.4.dylib',
      '/usr/lib/libobjc.A.dylib',
      '/usr/lib/libutil.dylib',
      '/usr/lib/system',
      '/usr/lib/system/libcache.dylib',
      '/usr/lib/system/libcommonCrypto.dylib',
      '/usr/lib/system/libcompiler_rt.dylib',
      '/usr/lib/system/libcopyfile.dylib',
      '/usr/lib/system/libcorecrypto.dylib',
      '/usr/lib/system/libdispatch.dylib',
      '/usr/lib/system/libdyld.dylib',
      '/usr/lib/system/libkeymgr.dylib',
      '/usr/lib/system/liblaunch.dylib',
      '/usr/lib/system/libmacho.dylib',
      '/usr/lib/system/libquarantine.dylib',
      '/usr/lib/system/libremovefile.dylib',
      '/usr/lib/system/libsystem_asl.dylib',
      '/usr/lib/system/libsystem_blocks.dylib',
      '/usr/lib/system/libsystem_c.dylib',
      '/usr/lib/system/libsystem_configuration.dylib',
      '/usr/lib/system/libsystem_coreservices.dylib',
      '/usr/lib/system/libsystem_coretls.dylib',
      '/usr/lib/system/libsystem_dnssd.dylib',
      '/usr/lib/system/libsystem_info.dylib',
      '/usr/lib/system/libsystem_kernel.dylib',
      '/usr/lib/system/libsystem_m.dylib',
      '/usr/lib/system/libsystem_malloc.dylib',
      '/usr/lib/system/libsystem_network.dylib',
      '/usr/lib/system/libsystem_networkextension.dylib',
      '/usr/lib/system/libsystem_notify.dylib',
      '/usr/lib/system/libsystem_platform.dylib',
      '/usr/lib/system/libsystem_pthread.dylib',
      '/usr/lib/system/libsystem_sandbox.dylib',
      '/usr/lib/system/libsystem_secinit.dylib',
      '/usr/lib/system/libsystem_stats.dylib',
      '/usr/lib/system/libsystem_trace.dylib',
      '/usr/lib/system/libunc.dylib',
      '/usr/lib/system/libunwind.dylib',
      '/usr/lib/system/libxpc.dylib',
    ])
    actual_files = file_find.find(tmp_dir, file_type = file_find.ANY, relative = True)
    actual_files = [ path.join('/', f) for f in actual_files ]
    self.assertEqual( expected_files, actual_files )

if __name__ == '__main__':
  pass #unit_test.main()
