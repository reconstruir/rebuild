#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from bes.testing.unit_test import unit_test
from bes.common import cached_property, dict_util, string_util
from bes.fs import file_find, temp_file
from bes.system import execute, os_env
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
  #DEBUG = True

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
    tm.ensure_tools(knife_desc)
    self.assertEqual( [
      'knife_6_6_6/linux-ubuntu-18/x86_64/db/packages.db',
      'knife_6_6_6/linux-ubuntu-18/x86_64/env/framework/bin/bes_path.py',
      'knife_6_6_6/linux-ubuntu-18/x86_64/env/framework/env/bes_framework.sh',
      'knife_6_6_6/linux-ubuntu-18/x86_64/env/framework/env/bes_path.sh',
      'knife_6_6_6/linux-ubuntu-18/x86_64/env/framework/env/bes_testing.sh',
      'knife_6_6_6/linux-ubuntu-18/x86_64/env/knife_env.sh',
      'knife_6_6_6/linux-ubuntu-18/x86_64/run.sh',
      'knife_6_6_6/linux-ubuntu-18/x86_64/setup.sh',
      'knife_6_6_6/linux-ubuntu-18/x86_64/stuff/bin/cut.exe',
      'knife_6_6_6/linux-ubuntu-18/x86_64/stuff/bin/cut.sh',
      'knife_6_6_6/linux-ubuntu-18/x86_64/stuff/bin/links_with_shared.exe',
      'knife_6_6_6/linux-ubuntu-18/x86_64/stuff/bin/links_with_static.exe',
      'knife_6_6_6/linux-ubuntu-18/x86_64/stuff/include/libfoo_shared.h',
      'knife_6_6_6/linux-ubuntu-18/x86_64/stuff/include/libfoo_static.h',
      'knife_6_6_6/linux-ubuntu-18/x86_64/stuff/lib/libfoo_shared.so',
      'knife_6_6_6/linux-ubuntu-18/x86_64/stuff/lib/libfoo_static.a',
      'knife_6_6_6/run.sh',
      'knife_6_6_6/setup.sh',
      ], file_find.find(tm.root_dir) )
    
  def test_use_shell_tool(self):
    tm, am, amt = self._make_test_tm()
    knife = PD.parse('knife-1.0.0')
    tm.ensure_tools(knife)
    rv = tm.run_tool(knife, [ 'cut.sh', 'a', 'b', '666' ], {})
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'cut.sh: a b 666', rv.stdout.strip() )

  def test_use_python_tool(self):
    tm, am, amt = self._make_test_tm()
    amt.add_recipes(self.RECIPES)
    amt.publish(self.DESCRIPTORS)
    cuchillo = PD.parse('cuchillo-1.0.0')
    tm.ensure_tools(cuchillo)
    rv = tm.run_tool(PD.parse('steel-1.0.0'), [ 'steel_exe.py', '6' ], {})
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'steel_exe.py: 16', rv.stdout.strip() )

  def test_use_binary_tool_static(self):
    tm, am, amt = self._make_test_tm()
    knife = PD.parse('knife-1.0.0')
    tm.ensure_tools(knife)
    rv = tm.run_tool(knife, [ 'links_with_static.exe' ], {})
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( '11', rv.stdout.strip() )
    
  def test_use_binary_tool_shared(self):
    tm, am, amt = self._make_test_tm()
    knife = PD.parse('knife-1.0.0')
    tm.ensure_tools(knife)
    rv = tm.run_tool(knife, [ 'links_with_shared.exe' ], {})
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( '22', rv.stdout.strip() )
    
  def test_transform_env(self):
    tm, am, amt = self._make_test_tm()
    amt.add_recipes(self.RECIPES)
    amt.publish(self.DESCRIPTORS)
    cuchillo = PD.parse('cuchillo-1.0.0')
    tm.ensure_tools(cuchillo)
    env = tm.transform_env({}, cuchillo)
    replacements = { tm.root_dir: '$ROOT_DIR' }
    env2 = copy.deepcopy(env)
    dict_util.replace_values(env2, replacements)
    self.assertEqual( {
      'WOOD_ENV1': 'wood_env1',
      'CUCHILLO_ENV1': 'cuchillo_env1',
      'STEEL_ENV1': 'steel_env1',
      'IRON_ENV1': 'iron_env1',
      'CARBON_ENV1': 'carbon_env1',
      'PATH': '/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:.:$ROOT_DIR/steel_1_0_0/linux-ubuntu-18/x86_64/stuff/bin',
      'PYTHONPATH': '$ROOT_DIR/steel_1_0_0/linux-ubuntu-18/x86_64/stuff/lib/python',
    }, env2 )

  def test_tool_installed_files(self):
    tm, am, amt = self._make_test_tm()
    amt.add_recipes(self.RECIPES)
    amt.publish(self.DESCRIPTORS)
    cuchillo = PD.parse('cuchillo-1.0.0')
    tm.ensure_tools(cuchillo)
    self.assertEqual( [
      'cuchillo_1_0_0/linux-ubuntu-18/x86_64/db/packages.db',
      'cuchillo_1_0_0/linux-ubuntu-18/x86_64/env/cuchillo_env.sh',
      'cuchillo_1_0_0/linux-ubuntu-18/x86_64/env/framework/bin/bes_path.py',
      'cuchillo_1_0_0/linux-ubuntu-18/x86_64/env/framework/env/bes_framework.sh',
      'cuchillo_1_0_0/linux-ubuntu-18/x86_64/env/framework/env/bes_path.sh',
      'cuchillo_1_0_0/linux-ubuntu-18/x86_64/env/framework/env/bes_testing.sh',
      'cuchillo_1_0_0/linux-ubuntu-18/x86_64/run.sh',
      'cuchillo_1_0_0/linux-ubuntu-18/x86_64/setup.sh',
      'cuchillo_1_0_0/linux-ubuntu-18/x86_64/stuff/bin/cuchillo.py',
      'cuchillo_1_0_0/run.sh',
      'cuchillo_1_0_0/setup.sh',
      'steel_1_0_0/linux-ubuntu-18/x86_64/db/packages.db',
      'steel_1_0_0/linux-ubuntu-18/x86_64/env/carbon_env.sh',
      'steel_1_0_0/linux-ubuntu-18/x86_64/env/framework/bin/bes_path.py',
      'steel_1_0_0/linux-ubuntu-18/x86_64/env/framework/env/bes_framework.sh',
      'steel_1_0_0/linux-ubuntu-18/x86_64/env/framework/env/bes_path.sh',
      'steel_1_0_0/linux-ubuntu-18/x86_64/env/framework/env/bes_testing.sh',
      'steel_1_0_0/linux-ubuntu-18/x86_64/env/iron_env.sh',
      'steel_1_0_0/linux-ubuntu-18/x86_64/env/steel_env.sh',
      'steel_1_0_0/linux-ubuntu-18/x86_64/run.sh',
      'steel_1_0_0/linux-ubuntu-18/x86_64/setup.sh',
      'steel_1_0_0/linux-ubuntu-18/x86_64/stuff/bin/carbon.py',
      'steel_1_0_0/linux-ubuntu-18/x86_64/stuff/bin/iron.py',
      'steel_1_0_0/linux-ubuntu-18/x86_64/stuff/bin/steel_exe.py',
      'steel_1_0_0/linux-ubuntu-18/x86_64/stuff/lib/python/easy-install.pth',
      'steel_1_0_0/linux-ubuntu-18/x86_64/stuff/lib/python/site.py',
      'steel_1_0_0/linux-ubuntu-18/x86_64/stuff/lib/python/steel.py',
      'steel_1_0_0/run.sh',
      'steel_1_0_0/setup.sh',
      'wood_1_0_0/linux-ubuntu-18/x86_64/db/packages.db',
      'wood_1_0_0/linux-ubuntu-18/x86_64/env/framework/bin/bes_path.py',
      'wood_1_0_0/linux-ubuntu-18/x86_64/env/framework/env/bes_framework.sh',
      'wood_1_0_0/linux-ubuntu-18/x86_64/env/framework/env/bes_path.sh',
      'wood_1_0_0/linux-ubuntu-18/x86_64/env/framework/env/bes_testing.sh',
      'wood_1_0_0/linux-ubuntu-18/x86_64/env/wood_env.sh',
      'wood_1_0_0/linux-ubuntu-18/x86_64/run.sh',
      'wood_1_0_0/linux-ubuntu-18/x86_64/setup.sh',
      'wood_1_0_0/linux-ubuntu-18/x86_64/stuff/bin/wood.py',
      'wood_1_0_0/run.sh',
      'wood_1_0_0/setup.sh',
      ], file_find.find(tm.root_dir) )
    
  RECIPES = '''
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
    bin/steel_exe.py
      \#!/usr/bin/env python
      import sys
      assert len(sys.argv) == 2
      import steel
      print('steel_exe.py: %d' % (steel.steel_func1(int(sys.argv[1]))))
      raise SystemExit(0)
    lib/python/steel.py
      def steel_func1(x):
        return x + 10

  env_files
    steel_env.sh
      \#@REBUILD_HEAD@
      export STEEL_ENV1=steel_env1
      bes_PATH_append ${REBUILD_STUFF_DIR}/bin
      bes_PYTHONPATH_append ${REBUILD_STUFF_DIR}/lib/python
      \#@REBUILD_TAIL@

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

  DESCRIPTORS = [
    'carbon;1.0.0;0;0;linux;release;x86_64;ubuntu;18',
    'cuchillo;1.0.0;0;0;linux;release;x86_64;ubuntu;18',
    'iron;1.0.0;0;0;linux;release;x86_64;ubuntu;18',
    'steel;1.0.0;0;0;linux;release;x86_64;ubuntu;18',
    'wood;1.0.0;0;0;linux;release;x86_64;ubuntu;18',
  ]
  
if __name__ == '__main__':
  unit_test.main()
