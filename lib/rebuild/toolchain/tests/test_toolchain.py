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

class test_toolchain_macos(unit_test):

  __unit_test_data_dir__ = 'test_data/toolchain'

  _DEBUG = True
  _DEBUG = False
  
  @skip_if(not _can_compile_macos(), 'cannot compile macos')
  def test_compile_cc(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self._DEBUG)
    if self._DEBUG:
      print('tmp_dir: %s' % (tmp_dir))
    source = r'''
#include <stdio.h>
int main(int argc, char* argv[])
{
  printf("%s::main()\n", __FILE__);
  return 0;
}
'''
    src = file_util.save(path.join(tmp_dir, 'test.c'), content = source)
    bt = build_target(system = System.MACOS)
    cc = compiler(bt)
    targets = cc.compile_c(src)
    self.assertEqual( 1, len(targets) )
    self.assertTrue( path.exists(targets[0][1]) )

class test_toolchain_ios(unit_test):

  __unit_test_data_dir__ = 'test_data/toolchain'

  _DEBUG = True
  _DEBUG = False
  
  @skip_if(not _can_compile_ios(), 'cannot compile ios')
  def test_compile_cc(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self._DEBUG)
    if self._DEBUG:
      print('tmp_dir: %s' % (tmp_dir))
    source = r'''
#include <stdio.h>
int main(int argc, char* argv[])
{
  printf("%s::main()\n", __FILE__);
}
'''
    src = file_util.save(path.join(tmp_dir, 'test.c'), content = source)
    bt = build_target(system = System.IOS)
    cc = compiler(bt)
    targets = cc.compile_c(src)
    self.assertEqual( 1, len(targets) )
    self.assertTrue( path.exists(targets[0][1]) )

class test_toolchain_android(unit_test):

  __unit_test_data_dir__ = 'test_data/toolchain'

  _DEBUG = True
  _DEBUG = False
  
  @skip_if(not _can_compile_android(), 'cannot compile android')
  def test_compile_cc(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self._DEBUG)
    if self._DEBUG:
      print('tmp_dir: %s' % (tmp_dir))
    source = r'''
#include <stdio.h>
int main(int argc, char* argv[])
{
  printf("%s::main()\n", __FILE__);
}
'''
    src = file_util.save(path.join(tmp_dir, 'test.c'), content = source)
    bt = build_target(system = System.ANDROID)
    cc = compiler(bt)
    targets = cc.compile_c(src)
    self.assertEqual( 1, len(targets) )
    self.assertTrue( path.exists(targets[0][1]) )
    
if __name__ == '__main__':
  unit_test.main()
