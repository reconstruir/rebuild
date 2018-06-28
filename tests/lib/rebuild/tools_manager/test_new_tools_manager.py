#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import script_unit_test
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

  TEST_BUILD_TARGET = build_target(build_system.LINUX, build_level.RELEASE)

  def _make_test_tm(self, am):
    root_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    tools_dir = path.join(root_dir, 'tools')
    if self.DEBUG:
      print("\ntools_dir:\n", tools_dir)
    return TM(tools_dir, am)

  def _make_test_artifact_manager(self):
    rt = rebuilder_tester(self._resolve_script(),
                          path.join(self.data_dir(), 'basic'),
                          path.normpath(path.join(self.data_dir(), '../sources')),
                          build_level.RELEASE,
                          debug = self.DEBUG)
    config = rebuilder_tester.config(bt = self.TEST_BUILD_TARGET)
    rv = rt.run(rebuilder_tester.config(), 'tfoo', 'tbar', 'tbaz')
    am_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print("\nam_dir:\n", am_dir)
    am = artifact_manager(am_dir, address = None, no_git = True)
    for artifact in rv.artifacts:
      am.publish(path.join(rv.artifacts_dir, artifact), self.TEST_BUILD_TARGET, False)
    return am
  
  def test_ensure_tool(self):
    am = self._make_test_artifact_manager()
    tm = self._make_test_tm(am)
    tfoo = PD.parse('tfoo-1.0.0')
    tbar = PD.parse('tbar-1.0.0')
    tbaz = PD.parse('tbaz-1.0.0')
    tm.ensure_tool(tfoo)
    env = tm.transform_env(tfoo, {})
    for k, v in env.items():
      print('CAA: %s: %s' % (k, v))
    print('bin_dir: %s' % (tm.bin_dir(tfoo)))
    
  def xtest_install_and_use_a_tool(self):
    tm = self._make_test_tm()
    am = self._make_test_artifact_manager()
    water_desc = PD.parse('water-1.0.0-0')
    packages = [
      water_desc
    ]
    tm.update(packages, am)
    tool_name = water_desc.name + '_script.sh'
    exe = tm.tool_exe(water_desc, tool_name)
    rv = execute.execute(exe)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( water_desc.full_name, rv.stdout.strip() )

if __name__ == '__main__':
  script_unit_test.main()
