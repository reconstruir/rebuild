#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.project.project_file import project_file
from rebuild.project.project_file_manager import project_file_manager as PFM
from bes.system import os_env_var
from bes.fs import file_util, temp_file
from bes.fs.testing import temp_content

class test_project_file_manager(unit_test):

  def test_env_project_files_unset(self):
    os_env_var('REBUILD_RECIPE_PATH').unset()
    self.assertEqual( [], PFM.find_env_project_files() )
    
  def test_env_project_files(self):
    tmp_dir = self._make_tmp_project_files()

    os_env_var('REBUILD_RECIPE_PATH').path = [
      path.join(tmp_dir, 'kiwi'),
      path.join(tmp_dir, 'orange'),
    ]

    try:
      self.assertEqual( [
        path.join(tmp_dir, 'kiwi/kiwi.reproject'),
        path.join(tmp_dir, 'orange/orange.reproject'),
      ], PFM.find_env_project_files() )
    finally:
      os_env_var('REBUILD_RECIPE_PATH').unset

  def _make_tmp_project_files(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print('tmp_dir: %s' % (tmp_dir))

    kiwi_project = '''!rebuild.project!
project kiwi
  recipes
    recipes/kiwi/mykiwi.recipe
'''
    tmp_kiwi_file = temp_file.make_temp_file(content = kiwi_project)
    
    orange_project = '''!rebuild.project!
project orange
  recipes
    recipes/orange/myorange.recipe

project lemon
  recipes
    recipes/lemon/mylemon.recipe
'''
    tmp_orange_file = temp_file.make_temp_file(content = orange_project)
    
    items = [
      'file kiwi/kiwi.reproject "{project_file}" 644'.format(project_file = tmp_kiwi_file),
      'file orange/orange.reproject "{project_file}" 644'.format(project_file = tmp_orange_file),
    ]
    temp_content.write_items(items, tmp_dir)
    return tmp_dir
      
if __name__ == '__main__':
  unit_test.main()
