#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild import build_target
from rebuild.toolchain import toolchain
from bes.fs import file_util, temp_file
from bes.system import host
from bes.common import Shell, variable

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
    bt = build_target()
    tc = toolchain.get_toolchain(bt)
    cenv = tc.compiler_environment()
    tmp_source_file = path.join(tmp_dir, 'test.c')
    tmp_object_file = path.join(tmp_dir, 'test.o')
    file_util.save(tmp_source_file, content = source)
    cmd = '$CC -c $(SRC) -o $(OBJ)'
    variables = {}
    variables.update(tc.compiler_environment())
    variables['SRC'] = tmp_source_file
    variables['OBJ'] = tmp_object_file
    cmd = variable.substitute(cmd, variables)
    Shell.execute(cmd)
    self.assertTrue( path.exists(tmp_object_file) )
    
if __name__ == '__main__':
  unit_test.main()
