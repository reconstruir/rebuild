#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os, os.path as path
from bes.testing.unit_test import unit_test
from bes.common import Shell
from bes.fs import file_util, temp_file
from rebuild import build_os_env

class test_bes_sudo_editor_py(unit_test):

  __SUDOERS_UBUNTU = '''#
# This file MUST be edited with the 'visudo' command as root.
#
# Please consider adding local content in /etc/sudoers.d/ instead of
# directly modifying this file.
#
# See the man page for details on how to write a sudoers file.
#
Defaults	env_reset
Defaults	mail_badpass
Defaults	secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin"

# Host alias specification

# User alias specification

# Cmnd alias specification

# User privilege specification
root	ALL=(ALL:ALL) ALL

# Members of the admin group may gain root privileges
%admin ALL=(ALL) ALL

# Allow members of group sudo to execute any command
%sudo	ALL=(ALL:ALL) ALL

# See sudoers(5) for more information on "#include" directives:

#includedir /etc/sudoers.d
'''

  __BES_SUDO_EDITOR_PY = path.normpath(path.join(path.dirname(__file__), '../../../../bin/rebuild_sudo_editor.py'))

  DEBUG = False
  #DEBUG = True
  
  def test_bes_sudo_editor_py(self):
    mode = 0o440
    sudoers_tmp = temp_file.make_temp_file(content = self.__SUDOERS_UBUNTU, delete = not self.DEBUG)
    os.chmod(sudoers_tmp, mode)
    cmd = [
      self.__BES_SUDO_EDITOR_PY,
      '--sudoers',
      sudoers_tmp,
      'chupacabra',
      '/usr/sbin/chroot',
      '1',
    ]
    rv = build_os_env.call_python_script(cmd)
    if rv.exit_code != 0:
      raise RuntimeError('Failed to exectute \"%s\": %s' % (' '.join(cmd), rv.stdout))
    self.assertEquals( 0, rv.exit_code )
    self.assertEquals( mode, file_util.mode(sudoers_tmp) )

    actual_content = file_util.read(sudoers_tmp, codec = 'utf-8')
    difference = actual_content.replace(self.__SUDOERS_UBUNTU, '').strip()
    self.assertEquals( 'chupacabra ALL = (root) NOPASSWD: /usr/sbin/chroot # bes_sudo:v1' , difference )

    cmd = [
      self.__BES_SUDO_EDITOR_PY,
      '--sudoers',
      sudoers_tmp,
      'tjefferson',
      '/bin/cat',
      '1',
    ]
    rv = build_os_env.call_python_script(cmd)
    if rv.exit_code != 0:
      raise RuntimeError('Failed to exectute \"%s\": %s' % (' '.join(cmd), rv.stdout))
    self.assertEquals( 0, rv.exit_code )
    actual_content = file_util.read(sudoers_tmp, codec = 'utf-8')
    difference = actual_content.replace(self.__SUDOERS_UBUNTU, '').strip()
    self.assertEquals( 'chupacabra ALL = (root) NOPASSWD: /usr/sbin/chroot # bes_sudo:v1\ntjefferson ALL = (root) NOPASSWD: /bin/cat # bes_sudo:v1' , difference )

if __name__ == '__main__':
  unit_test.main()
