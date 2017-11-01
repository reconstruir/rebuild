#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild import build_target
from rebuild.toolchain import compiler, toolchain
from bes.fs import file_util, temp_file
from bes.system import host
from bes.common import object_util, Shell, variable

class test_toolchain(unit_test):

  __unit_test_data_dir__ = 'test_data/toolchain'

  _DEBUG = True
  _DEBUG = False
  
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
    bt = build_target()
    cc = compiler(bt)
    targets = cc.compile_c(src)
    self.assertEqual( 1, len(targets) )
    self.assertTrue( path.exists(targets[0][1]) )
    
if __name__ == '__main__':
  unit_test.main()
