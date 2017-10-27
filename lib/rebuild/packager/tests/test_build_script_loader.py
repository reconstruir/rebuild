#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file
from rebuild.packager.build_script_loader import build_script_loader
from rebuild import build_target

class test_build_script_loader(unit_test):

  __unit_test_data_dir__ = 'test_data/build_script'

  def test_load_libjpeg(self):
    filenames = [ self.data_path('build_libjpeg.py') ]
    bt = build_target()
    scripts = build_script_loader.load(filenames[0], bt)
    self.assertEqual( 1, len(scripts) )
    self.assertEqual( 'libjpeg', scripts[0].descriptor.name )
    self.assertEqual( ( '9a', 1, 0), scripts[0].descriptor.version )

  def test_multiple_recipes(self):
    filenames = [ self.data_path('build_multiple_recipes.py') ]
    bt = build_target()
    scripts = build_script_loader.load(filenames[0], bt)
    self.assertEqual( 4, len(scripts) )

    self.assertEqual( 'libsdl2', scripts[0].descriptor.name )
    self.assertEqual( ( '2.0.5', 0, 0), scripts[0].descriptor.version )
    self.assertEqual( 'libsdl2_image', scripts[1].descriptor.name )
    self.assertEqual( ( '2.0.1', 0, 0), scripts[1].descriptor.version )
    self.assertEqual( 'libsdl2_image', scripts[1].descriptor.name )
    self.assertEqual( ( '2.0.1', 0, 0), scripts[1].descriptor.version )
    self.assertEqual( 'libsdl2_mixer', scripts[2].descriptor.name )
    self.assertEqual( ( '2.0.1', 0, 0), scripts[2].descriptor.version )
    self.assertEqual( 'libsdl2_ttf', scripts[3].descriptor.name )
    self.assertEqual( ( '2.0.13', 0, 0), scripts[3].descriptor.version )

if __name__ == '__main__':
  unit_test.main()
