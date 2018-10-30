#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import script_unit_test
from bes.common import cached_property
from bes.fs import temp_file
from bes.system import execute
from rebuild.base import build_target, build_system, build_level, package_descriptor as PD
from rebuild.package import artifact_manager
from rebuild.tools_manager import new_tools_manager as TM
from _rebuild_testing.fake_package_unit_test import fake_package_unit_test as FPUT

from _rebuild_testing.rebuilder_tester import rebuilder_tester

class test_new_tools_manager(script_unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/rebuilder'
  __script__ = __file__, '../../../../bin/rebuilder.py'
  
  DEBUG = script_unit_test.DEBUG
  #DEBUG = True

  TEST_BUILD_TARGET = build_target.parse_path('linux-ubuntu-18/x86_64/release')

  @classmethod
  def _make_test_artifact_manager(clazz):
    mutations = { 'system': 'linux', 'distro': 'ubuntu', 'distro_version': '18' }
    return FPUT.make_artifact_manager(debug = clazz.DEBUG,
                                      recipes = clazz._RECIPES,
                                      build_target = clazz.TEST_BUILD_TARGET,
                                      mutations = mutations)
  
  def _make_test_tm(self):
    root_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    tools_dir = path.join(root_dir, 'tools')
    am = self._make_test_artifact_manager()
    if self.DEBUG:
      print('\ntools_manager dir:\n%s' % (tools_dir))
    return TM(tools_dir, self.TEST_BUILD_TARGET, am)

  def test_ensure_tool(self):
    tm = self._make_test_tm()
    knife_desc = PD.parse('knife-6.6.6')
    tm.ensure_tool(knife_desc)
    self.assertTrue( path.exists(tm.tool_exe(knife_desc, 'cut.sh')) )
    
  def test_use_shell_tool(self):
    tm = self._make_test_tm()
    knife_desc = PD.parse('knife-6.6.6')
    tm.ensure_tool(knife_desc)
    exe = tm.tool_exe(knife_desc, 'cut.sh')
    rv = execute.execute([ exe, 'a', 'b', '666' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'cut.sh: a b 666', rv.stdout.strip() )

  def test_use_binary_tool(self):
    tm = self._make_test_tm()
    knife_desc = PD.parse('knife-6.6.6')
    tm.ensure_tool(knife_desc)
    exe = tm.tool_exe(knife_desc, 'cut.exe')
    rv = execute.execute([ exe, 'a', 'b', '666' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'cut.exe: a b 666', rv.stdout.strip() )

  def xtest_one_tool_env(self):
    tm = self._make_test_tm()
    tfoo = PD.parse('tfoo-1.0.0')
    tm.ensure_tool(tfoo)
    env = tm.transform_env(tfoo, {})
    self.assertEqual( 'tfoo_env1', env['TFOO_ENV1'] )
    self.assertEqual( 'tfoo_env2', env['TFOO_ENV2'] )
    
  def xtest_ensure_tools(self):
    tm = self._make_test_tm()
    tfoo = PD.parse('tfoo-1.0.0')
    tbar = PD.parse('tbar-1.0.0')
    tbaz = PD.parse('tbaz-1.0.0')
    tm.ensure_tools([ tfoo, tbar, tbaz ])
    env = tm.transform_env(tfoo, {})
    for k, v in env.items():
      print('CAA: %s: %s' % (k, v))
    print('bin_dir: %s' % (tm.bin_dir(tfoo,)))

  def xtest_many_tool_env(self):
    tm = self._make_test_tm()
    tfoo = PD.parse('tfoo-1.0.0')
    tbar = PD.parse('tbar-1.0.0')
    tbaz = PD.parse('tbaz-1.0.0')
    tm.ensure_tools([ tfoo, tbar, tbaz ])
    env = tm.transform_env(tfoo, {})
    self.assertEqual( 'tfoo_env1', env['TFOO_ENV1'] )
    self.assertEqual( 'tfoo_env2', env['TFOO_ENV2'] )

  _RECIPES = '''
fake_package knife 6.6.6 0 0 linux release x86_64 ubuntu 18
  files
    bin/cut.sh
      \#!/bin/sh
      echo cut.sh: ${1+"$@"} ; exit 0
  c_program
    bin/cut.exe
      sources
        main.c
          \#include <stdio.h>
          int main(int argc, char* argv[]) {
            char** arg;
            if (argc < 2) {
              fprintf(stderr, "Usage: cut.exe args\\n");
              return 1;
            }
            fprintf(stdout, "cut.exe: ");
            for(arg = argv + 1; *arg != NULL; ++arg) {
              fprintf(stdout, "%s ", *arg);
            }
            fprintf(stdout, "\\n");
            return 0;
          }
  static_c_library
    lib/libfoo.a
      sources
        foo.c
          int foo(int x) {
            return x + 1;
          }
      headers
        foo.h
          \#ifndef __FOO_H__
          \#define __FOO_H__
          extern int foo(int x);
          \#endif /* __FOO_H__ */

'''
###  c_program
###    bin/cut.exe
###      sources
###        main.c
###          \#include <stdio.h>
###          int main(int argc, char* argv[]) {
###            char* arg;
###            if (argc < 2) {
###              fprintf(stderr, "Usage: cut.exe args\n");
###              return 1;
###            }
###            fprintf(stdout, "cut.exe:");
###            for(arg = argv[1]; arg != NULL; arg++) {
###              fprintf(stdout, "%s", arg);
###            }
###            fprintf(stdout, "\n");
###            return 0;
###          }
  
  x_RECIPES = '''
fake_package knife 1.0.0 0 0 linux release x86_64 ubuntu 18
  files
    bin/cut.sh
     \#!/bin/bash
      echo cut: ${1+"$@"}; exit 0
###    static_c_library
###      headers
###        libknife/knife.h
###          \#ifndef __KNIFE_H__
###          \#define __KNIFE_H__
###          extern int cut(int depth);
###          \#endif /* __KNIFE_H__ */
###      sources
###        knife.c
###          \#include <libknife/knife.h>
###          int cut(int depth) {
###            if (depth < 0 or depth > 10) {
###              fprintf(stderr, "Invalid depth: %d\n", depth);
###              return 1;
###            }
###            printf("cut depth %d\n", depth);
###            return 0;
###          }
'''
  
if __name__ == '__main__':
  script_unit_test.main()
