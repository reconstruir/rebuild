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
from rebuild.package.unit_test_packages import unit_test_packages

from _rebuild_testing.rebuilder_tester import rebuilder_tester

class test_new_tools_manager(script_unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/rebuilder'
  __script__ = __file__, '../../../../bin/rebuilder.py'
  
  DEBUG = script_unit_test.DEBUG
  #DEBUG = True

  TEST_BUILD_TARGET = build_target.parse_path('linux-ubuntu-18/x86_64/release')

  @cached_property
  def artifact_manager(self):
    rt = rebuilder_tester(self._resolve_script(),
                          path.join(self.data_dir(), 'basic'),
                          path.normpath(path.join(self.data_dir(), '../sources')),
                          build_level.RELEASE,
                          debug = self.DEBUG)
    config = rebuilder_tester.config(bt = self.TEST_BUILD_TARGET)
    rv = rt.run(rebuilder_tester.config(), 'tfoo', 'tbar', 'tbaz')
    am_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print('\nartifact_manager dir:\n%s' % (am_dir))
    am = artifact_manager(am_dir)
    for artifact in rv.artifacts:
      am.publish(path.join(rv.artifacts_dir, artifact), self.TEST_BUILD_TARGET, False)
    return am
  
  def _make_test_tm(self):
    root_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    tools_dir = path.join(root_dir, 'tools')
    if self.DEBUG:
      print('\ntools_manager dir:\n%s' % (tools_dir))
    return TM(tools_dir, self.artifact_manager)

  def test_ensure_tool(self):
    tm = self._make_test_tm()
    tfoo = PD.parse('tfoo-1.0.0')
    tm.ensure_tool(tfoo)
    self.assertTrue( path.exists(tm.tool_exe(tfoo, 'tfoo.py')) )
    
  def test_use_tool(self):
    tm = self._make_test_tm()
    tfoo = PD.parse('tfoo-1.0.0')
    tm.ensure_tool(tfoo)
    exe = tm.tool_exe(tfoo, 'tfoo.py')
    rv = execute.execute([ exe, 'a', 'b', '666' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'tfoo: a b 666', rv.stdout.strip() )

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
    
    
if __name__ == '__main__':
  script_unit_test.main()
