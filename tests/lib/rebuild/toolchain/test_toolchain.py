#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.base.build_system import build_system
from rebuild.base.build_target import build_target
from rebuild.toolchain.compiler import compiler
from rebuild.toolchain.toolchain import toolchain
from rebuild.toolchain.toolchain_testing import toolchain_testing
from bes.system.host import host
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.common.object_util import object_util
from bes.common.variable import variable
from bes.testing.unit_test_skip import skip_if

class test_toolchain(unit_test):

  DEBUG = False
  #DEBUG = True

  CC_SOURCE = r'''
#include <stdio.h>
int main(int argc, char* argv[])
{
  printf("%s::main()\n", __FILE__);
  return 0;
}
'''

  @skip_if(not toolchain_testing.can_compile_macos(), 'cannot compile macos')
  def test_compile_cc_macos(self):
    tmp_dir = self._make_temp_dir()
    src = self._make_temp_source(tmp_dir, 'test.c', self.CC_SOURCE)
    cc = self._make_compiler(build_system.MACOS, 'x86_64')
    targets = cc.compile_c(src)
    self.assertEqual( 1, len(targets) )
    self.assertTrue( path.exists(targets[0][1]) )

  @skip_if(not toolchain_testing.can_compile_ios(), 'cannot compile ios')
  def test_compile_cc_ios(self):
    tmp_dir = self._make_temp_dir()
    src = self._make_temp_source(tmp_dir, 'test.c', self.CC_SOURCE)
    cc = self._make_compiler(build_system.IOS, 'arm64')
    targets = cc.compile_c(src)
    self.assertEqual( 1, len(targets) )
    self.assertTrue( path.exists(targets[0][1]) )

  @skip_if(not toolchain_testing.can_compile_android(), 'cannot compile android')
  def test_compile_cc_android(self):
    tmp_dir = self._make_temp_dir()
    src = self._make_temp_source(tmp_dir, 'test.c', self.CC_SOURCE)
    cc = self._make_compiler(build_system.ANDROID, 'armv7')
    targets = cc.compile_c(src)
    self.assertEqual( 1, len(targets) )
    self.assertTrue( path.exists(targets[0][1]) )
    
  @skip_if(not toolchain_testing.can_compile_linux(), 'cannot compile linux')
  def test_compile_cc_linux(self):
    tmp_dir = self._make_temp_dir()
    src = self._make_temp_source(tmp_dir, 'test.c', self.CC_SOURCE)
    cc = self._make_compiler(build_system.LINUX, host.ARCH)
    targets = cc.compile_c(src)
    self.assertEqual( 1, len(targets) )
    self.assertTrue( path.exists(targets[0][1]) )
    
  @classmethod
  def _make_temp_dir(clazz):
    tmp_dir = temp_file.make_temp_dir(delete = not clazz.DEBUG)
    if clazz.DEBUG:
      print('tmp_dir: %s' % (tmp_dir))
    return tmp_dir

  @classmethod
  def _make_temp_source(clazz, tmp_dir, filename, content):
    return file_util.save(path.join(tmp_dir, filename), content = content)

  @classmethod
  def _make_compiler(clazz, system, arch):
    return compiler(build_target(system, '', '', '', arch, 'release'))

if __name__ == '__main__':
  unit_test.main()
