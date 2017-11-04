#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file
from rebuild.packager.build_recipe_loader import build_recipe_loader
from rebuild.base import build_target

class test_build_recipe_loader(unit_test):

  __unit_test_data_dir__ = 'test_data/build_script'

  def test_load_libjpeg(self):
    filenames = [ self.data_path('build_libjpeg.py') ]
    bt = build_target()
    recipes = build_recipe_loader.load(filenames[0], bt)
    self.assertEqual( 1, len(recipes) )
    self.assertEqual( 'libjpeg', recipes[0].descriptor.name )
    self.assertEqual( ( '9a', 1, 0), recipes[0].descriptor.version )

  def test_multiple_recipes(self):
    filenames = [ self.data_path('build_multiple_recipes.py') ]
    bt = build_target()
    recipes = build_recipe_loader.load(filenames[0], bt)
    self.assertEqual( 4, len(recipes) )

    self.assertEqual( 'libsdl2', recipes[0].descriptor.name )
    self.assertEqual( ( '2.0.5', 0, 0), recipes[0].descriptor.version )
    self.assertEqual( 'libsdl2_image', recipes[1].descriptor.name )
    self.assertEqual( ( '2.0.1', 0, 0), recipes[1].descriptor.version )
    self.assertEqual( 'libsdl2_image', recipes[1].descriptor.name )
    self.assertEqual( ( '2.0.1', 0, 0), recipes[1].descriptor.version )
    self.assertEqual( 'libsdl2_mixer', recipes[2].descriptor.name )
    self.assertEqual( ( '2.0.1', 0, 0), recipes[2].descriptor.version )
    self.assertEqual( 'libsdl2_ttf', recipes[3].descriptor.name )
    self.assertEqual( ( '2.0.13', 0, 0), recipes[3].descriptor.version )

if __name__ == '__main__':
  unit_test.main()
