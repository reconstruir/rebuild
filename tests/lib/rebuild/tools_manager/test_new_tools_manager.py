#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.common import cached_property
from bes.fs import temp_file
from bes.system import execute
from rebuild.base import build_target, build_system, build_level, package_descriptor as PD
from rebuild.tools_manager import new_tools_manager as TM
from _rebuild_testing.fake_package_unit_test import fake_package_unit_test as FPUT
from _rebuild_testing.fake_package_recipes import fake_package_recipes as RECIPES
from _rebuild_testing.artifact_manager_tester import artifact_manager_tester as AMT

from _rebuild_testing.rebuilder_tester import rebuilder_tester

class test_new_tools_manager(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/rebuilder'
  __script__ = __file__, '../../../../bin/rebuilder.py'
  
  DEBUG = unit_test.DEBUG
  DEBUG = True

  TEST_BUILD_TARGET = build_target.parse_path('linux-ubuntu-18/x86_64/release')

  def _make_test_tm(self):
    amt = AMT(recipes = RECIPES.KNIFE, debug = self.DEBUG)
    amt.publish('knife;6.6.6;0;0;linux;release;x86_64;ubuntu;18')
    root_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    tools_dir = path.join(root_dir, 'tools')
    if self.DEBUG:
      print('\ntools_manager dir:\n%s' % (tools_dir))
    return TM(tools_dir, self.TEST_BUILD_TARGET, amt.am), amt.am, amt

  def test_ensure_tool(self):
    tm, am, amt = self._make_test_tm()
    knife_desc = PD.parse('knife-6.6.6')
    tm.ensure_tool(knife_desc)
    self.assertTrue( path.exists(tm.tool_exe(knife_desc, 'cut.sh')) )
    
  def test_use_shell_tool(self):
    tm, am, amt = self._make_test_tm()
    knife_desc = PD.parse('knife-6.6.6')
    tm.ensure_tool(knife_desc)
    exe = tm.tool_exe(knife_desc, 'cut.sh')
    rv = execute.execute([ exe, 'a', 'b', '666' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'cut.sh: a b 666', rv.stdout.strip() )

  def test_use_binary_tool(self):
    tm, am, amt = self._make_test_tm()
    knife_desc = PD.parse('knife-6.6.6')
    tm.ensure_tool(knife_desc)
    exe = tm.tool_exe(knife_desc, 'cut.exe')
    rv = execute.execute([ exe, 'a', 'b', '666' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'cut.exe: a b 666', rv.stdout.strip() )

    exe = tm.tool_exe(knife_desc, 'links_with_static.exe')
    rv = execute.execute([ exe ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( '11', rv.stdout.strip() )

  def test_tool_env(self):
    recipes = '''
fake_package wood 1.0.0 0 0 linux release x86_64 ubuntu 18
  files
    bin/wood.py
      \#!/usr/bin/env python
      print('ffoo')
      raise SystemExit(0)

  env_files
    wood_env.sh
      export WOOD_ENV1=wood_env1

fake_package iron 1.0.0 0 0 linux release x86_64 ubuntu 18
  files
    bin/iron.py
      \#!/usr/bin/env python
      print('fbar')
      raise SystemExit(0)

  env_files
    iron_env.sh
      export IRON_ENV1=iron_env1

fake_package carbon 1.0.0 0 0 linux release x86_64 ubuntu 18
  files
    bin/carbon.py
      \#!/usr/bin/env python
      print('fbar')
      raise SystemExit(0)

  env_files
    carbon_env.sh
      export CARBON_ENV1=carbon_env1

fake_package steel 1.0.0 0 0 linux release x86_64 ubuntu 18
  files
    bin/steel.py
      \#!/usr/bin/env python
      print('fbar')
      raise SystemExit(0)

  env_files
    steel_env.sh
      export STEEL_ENV1=steel_env1

  requirements
    all: RUN iron >= 1.0.0
    all: RUN carbon >= 1.0.0

fake_package cuchillo 1.0.0 0 0 linux release x86_64 ubuntu 18
  files
    bin/cuchillo.py
      \#!/usr/bin/env python
      print('fbaz')
      raise SystemExit(0)

  env_files
    cuchillo_env.sh
      export CUCHILLO_ENV1=cuchillo_env1

  requirements
    all: TOOL wood >= 1.0.0
    all: TOOL steel >= 1.0.0

'''
    tm, am, amt = self._make_test_tm()
    amt.add_recipes(recipes)
    amt.publish('carbon;1.0.0;0;0;linux;release;x86_64;ubuntu;18')
    amt.publish('cuchillo;1.0.0;0;0;linux;release;x86_64;ubuntu;18')
    amt.publish('iron;1.0.0;0;0;linux;release;x86_64;ubuntu;18')
    amt.publish('steel;1.0.0;0;0;linux;release;x86_64;ubuntu;18')
    amt.publish('wood;1.0.0;0;0;linux;release;x86_64;ubuntu;18')
    cuchillo = PD.parse('cuchillo-1.0.0')
    tm.ensure_tool(cuchillo)
    env = tm.transform_env(cuchillo, {})
    self.assertEqual( {
      'WOOD_ENV1': 'wood_env1',
      'CUCHILLO_ENV1': 'cuchillo_env1',
      'STEEL_ENV1': 'steel_env1',
      'IRON_ENV1': 'iron_env1',
      'CARBON_ENV1': 'carbon_env1',
    }, env )
    
  def xtest_use_binary_tool_with_shared_lib(self):
    tm, am, amt = self._make_test_tm()
    knife_desc = PD.parse('knife-6.6.6')
    tm.ensure_tool(knife_desc)
    exe = tm.tool_exe(knife_desc, 'links_with_shared.exe')
    rv = execute.execute([ exe ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( '11', rv.stdout.strip() )
    
  def xtest_one_tool_env(self):
    tm, am, amt = self._make_test_tm()
    tfoo = PD.parse('tfoo-1.0.0')
    tm.ensure_tool(tfoo)
    env = tm.transform_env(tfoo, {})
    self.assertEqual( 'tfoo_env1', env['TFOO_ENV1'] )
    self.assertEqual( 'tfoo_env2', env['TFOO_ENV2'] )
    
  def xtest_ensure_tools(self):
    tm, am, amt = self._make_test_tm()
    tfoo = PD.parse('tfoo-1.0.0')
    tbar = PD.parse('tbar-1.0.0')
    tbaz = PD.parse('tbaz-1.0.0')
    tm.ensure_tools([ tfoo, tbar, tbaz ])
    env = tm.transform_env(tfoo, {})
    for k, v in env.items():
      print('CAA: %s: %s' % (k, v))
    print('bin_dir: %s' % (tm.bin_dir(tfoo,)))

  def xtest_many_tool_env(self):
    tm, am, amt = self._make_test_tm()
    tfoo = PD.parse('tfoo-1.0.0')
    tbar = PD.parse('tbar-1.0.0')
    tbaz = PD.parse('tbaz-1.0.0')
    tm.ensure_tools([ tfoo, tbar, tbaz ])
    env = tm.transform_env(tfoo, {})
    self.assertEqual( 'tfoo_env1', env['TFOO_ENV1'] )
    self.assertEqual( 'tfoo_env2', env['TFOO_ENV2'] )

if __name__ == '__main__':
  unit_test.main()
