#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild import build_target
from rebuild.toolchain import toolchain
from bes.fs import file_util, temp_file
from bes.system import host

class test_toolchain(unit_test):

  __unit_test_data_dir__ = 'test_data/toolchain'

  _DEBUG = True
  _DEBUG = False
  
  def test_compile_cc(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self._DEBUG)
    source = '''
#include <stdio.h>
int main(int argc, char* argv[])
{
  printf("%s::main()\n", __FILE__);
}
'''
    bt = build_target()
    cenv = toolchain.compiler_environment(bt)
    tmp_source_file = path.join(tmp_dir, 'test.c')
    file_util.save(tmp_source_file, content = source)
    cmd = '$CC -c $SOURCE -o $@'

    variables = {}
    variables.update(toolchain.compiler_environment(bt))

    print(variables)

'''    
  @skip_if(not host.is_macos(), 'not macos')
  def test_dependencies_macos(self):
    deps = library.dependencies('/bin/bash')
    self.assertEquals( 2, len(deps) )
    self.assertTrue( path.basename(deps[0]).startswith('libSystem') )
    self.assertTrue( path.basename(deps[1]).startswith('libncurses') )
'''

if __name__ == '__main__':
  unit_test.main()
