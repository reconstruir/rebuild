#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.project.project_file import project_file
from rebuild.project.project_file_manager import project_file_manager as PFM
from bes.build.build_target import build_target as BT
from bes.system.os_env import os_env_var
from bes.fs.file_util import file_util
from bes.fs.testing.temp_content import temp_content

class test_project_file_manager(unit_test):

  def test_env_project_files_unset(self):
    os_env_var('REBUILD_RECIPE_PATH').unset()
    self.assertEqual( [], PFM.find_env_project_files() )
    
  def test_env_project_files(self):
    tmp_dir = self._make_tmp_project_files()

    os_env_var('REBUILD_RECIPE_PATH').path = [
      path.join(tmp_dir, 'fructose'),
      path.join(tmp_dir, 'kiwi'),
      path.join(tmp_dir, 'orange'),
    ]

    try:
      self.assertEqual( [
        path.join(tmp_dir, self.xp_filename('fructose/fructose.reproject')),
        path.join(tmp_dir, self.xp_filename('kiwi/kiwi.reproject')),
        path.join(tmp_dir, self.xp_filename('orange/orange.reproject')),
      ], PFM.find_env_project_files() )
    finally:
      os_env_var('REBUILD_RECIPE_PATH').unset

  def test_load_project_file(self):
    tmp_dir = self._make_tmp_project_files()
    bt = BT.parse_path('macos-10.10/x86_64/release')
    p = PFM()
    p.load_project_file(path.join(tmp_dir, 'fructose/fructose.reproject'))
    p.load_project_file(path.join(tmp_dir, 'kiwi/kiwi.reproject'))
    p.load_project_file(path.join(tmp_dir, 'orange/orange.reproject'))

    smoothie_project = '''!rebuild.project!
project smoothie
  recipes
    recipes/smoothie/mysmoothie.recipe
  imports
    kiwi
'''
    smoothie_pf = self.make_temp_file(content = smoothie_project)
    p.load_project_file(smoothie_pf)
    available = p.available_recipes(smoothie_pf, bt)
    for r in available:
      print('RECIPE: %s' % (str(r)))
      
    #p.print_projects()
    #p.print_dep_map()
    
  def _make_tmp_project_files(self):
    tmp_dir = self.make_temp_dir()

    fructose_project = '''!rebuild.project!
project fructose
  recipes
    recipes/fructose/myfructose.recipe
'''
      
    kiwi_project = '''!rebuild.project!
project kiwi
  recipes
    recipes/kiwi/mykiwi.recipe
  imports
    fructose

project citrus
  recipes
    recipes/citrus/mycitrus.recipe
'''
    
    orange_project = '''!rebuild.project!
project orange
  recipes
    recipes/orange/myorange.recipe
  imports
    fructose

project lemon
  recipes
    recipes/lemon/mylemon.recipe
  imports
    fructose
    citrus
'''
    
    items = [
      'file fructose/fructose.reproject "file:{}" 644'.format(self.make_temp_file(content = fructose_project)),
      'file kiwi/kiwi.reproject "file:{}" 644'.format(self.make_temp_file(content = kiwi_project)),
      'file orange/orange.reproject "file:{}" 644'.format(self.make_temp_file(content = orange_project)),
    ]
    temp_content.write_items(items, tmp_dir)
    return tmp_dir
      
if __name__ == '__main__':
  unit_test.main()
