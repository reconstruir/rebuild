#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild import build_target, System
from rebuild.toolchain import compiler, toolchain
from bes.fs import file_util, temp_file
from bes.system import host
from bes.common import object_util, Shell, variable
from bes.testing.unit_test.unit_test_skip import skip_if

def _can_compile_macos(): return host.is_macos()
def _can_compile_ios(): return host.is_macos()
def _android_toolchain_is_valid(): return toolchain.get_toolchain(build_target(system = System.ANDROID)).is_valid()
def _can_compile_android(): return (host.is_macos() or host.is_linux()) and _android_toolchain_is_valid()
def _can_compile_linux(): return host.is_linux()

class test_toolchain(unit_test):

  __unit_test_data_dir__ = 'test_data/toolchain'

  _DEBUG = True
  _DEBUG = False

  CC_SOURCE = r'''
#include <stdio.h>
int main(int argc, char* argv[])
{
  printf("%s::main()\n", __FILE__);
  return 0;
}
'''

  @skip_if(not _can_compile_macos(), 'cannot compile macos')
  def test_compile_cc_macos(self):
    tmp_dir = self._make_temp_dir()
    src = self._make_temp_source(tmp_dir, 'test.c', self.CC_SOURCE)
    cc = self._make_compiler(System.MACOS)
    targets = cc.compile_c(src)
    self.assertEqual( 1, len(targets) )
    self.assertTrue( path.exists(targets[0][1]) )

  @skip_if(not _can_compile_ios(), 'cannot compile ios')
  def test_compile_cc_ios(self):
    tmp_dir = self._make_temp_dir()
    src = self._make_temp_source(tmp_dir, 'test.c', self.CC_SOURCE)
    cc = self._make_compiler(System.IOS)
    targets = cc.compile_c(src)
    self.assertEqual( 1, len(targets) )
    self.assertTrue( path.exists(targets[0][1]) )

  @skip_if(not _can_compile_android(), 'cannot compile android')
  def test_compile_cc_android(self):
    tmp_dir = self._make_temp_dir()
    src = self._make_temp_source(tmp_dir, 'test.c', self.CC_SOURCE)
    cc = self._make_compiler(System.ANDROID)
    targets = cc.compile_c(src)
    self.assertEqual( 1, len(targets) )
    self.assertTrue( path.exists(targets[0][1]) )
    
  @skip_if(not _can_compile_linux(), 'cannot compile linux')
  def test_compile_cc_linux(self):
    tmp_dir = self._make_temp_dir()
    src = self._make_temp_source(tmp_dir, 'test.c', self.CC_SOURCE)
    cc = self._make_compiler(System.LINUX)
    targets = cc.compile_c(src)
    self.assertEqual( 1, len(targets) )
    self.assertTrue( path.exists(targets[0][1]) )
    
  @classmethod
  def _make_temp_dir(clazz):
    tmp_dir = temp_file.make_temp_dir(delete = not clazz._DEBUG)
    if clazz._DEBUG:
      print('tmp_dir: %s' % (tmp_dir))
    return tmp_dir

  @classmethod
  def _make_temp_source(clazz, tmp_dir, filename, content):
    return file_util.save(path.join(tmp_dir, filename), content = content)

  @classmethod
  def _make_compiler(clazz, system):
    return compiler(build_target(system = system))

if __name__ == '__main__':
  unit_test.main()
