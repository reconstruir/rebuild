#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file
from rebuild.builder import builder, builder_config, builder_env
from rebuild.builder.unit_test_packaging import unit_test_packaging
from rebuild.source_finder import local_source_finder, source_finder_chain
from bes.git import git_download_cache
from rebuild.checksum import checksum_manager

class test_builder(unit_test):

  __unit_test_data_dir__ = '../../test_data/packager'

  DEBUG = False
#  DEBUG = True
  
  def test_amhello(self):
    tmp_dir = temp_file.make_temp_dir()
    amhello_builder_script = unit_test_packaging.make_recipe_v1(tmp_dir, 'build_amhello.py', 'amhello', '1.0', 0)
    file_util.copy(self.data_path('amhello-1.0.tar.gz'), tmp_dir)
    filenames = [ amhello_builder_script ]
    config = builder_config()
    config.build_root = path.join(tmp_dir, 'BUILD')
    config.source_dir = self.data_dir()
    config.no_network = True
    config.verbose = True
    env = builder_env(config, filenames)
    bldr = builder(env)
    packages = [ 'amhello' ]
    rv = bldr.build_many_scripts(packages)
    self.assertEqual( bldr.EXIT_CODE_SUCCESS, rv )

  def test_libpng(self):
    tmp_dir = temp_file.make_temp_dir()
    filenames = [ self.data_path('zlib/build_zlib.py'), self.data_path('libpng/build_libpng.py') ]
    config = builder_config()
    config.build_root = path.join(tmp_dir, 'BUILD')
    config.no_network = True
    config.source_dir = self.data_dir()
    env = builder_env(config, filenames)
    bldr = builder(env)
    packages = [ 'zlib', 'libpng' ]
    rv = bldr.build_many_scripts(packages)
    self.assertEqual( bldr.EXIT_CODE_SUCCESS, rv )

  def test_fructose(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print("tmp_dir: ", tmp_dir)
    data_files = [
      'build_fructose.py',
      'fructose-3.4.5.tar.gz',
      'fructose-test.c',
    ]

    for f in data_files:
      file_util.copy(self.data_path(f), tmp_dir)

    filenames = [ path.join(tmp_dir, 'build_fructose.py') ]
    config = builder_config()
    config.build_root = path.join(tmp_dir, 'BUILD')
    config.no_network = True
    config.source_dir = self.data_dir()
    env = builder_env(config, filenames)
    bldr = builder(env)
    packages_to_build = [ 'fructose' ]
    rv = bldr.build_many_scripts(packages_to_build)
    self.assertEqual( bldr.EXIT_CODE_SUCCESS, rv )
    
  def xxxtest_orange(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print("tmp_dir: ", tmp_dir)
    orange_requirements = [
      'all: fructose >= 3.4.5-6',
      'all: fiber >= 1.0.0-0',
    ]
    orange_builder_script = unit_test_packaging.make_recipe_v1(tmp_dir, 'build_orange.py', 'orange', '6.5.4', 3,
                                                                requirements = orange_requirements,
                                                                tests = [ 'all: orange-test.c' ])
    fructose_builder_script = unit_test_packaging.make_recipe_v1(tmp_dir, 'build_fructose.py', 'fructose', '3.4.5', 6,
                                                                  tests = [ 'all: fructose-test.c' ])
    fiber_builder_script = unit_test_packaging.make_recipe_v1(tmp_dir, 'build_fiber.py', 'fiber', '1.0.0', 0,
                                                               tests = [ 'all: fiber-test.c' ])

    data_files = [
      'fiber-1.0.0.tar.gz',
      'fructose-3.4.5.tar.gz',
      'orange-6.5.4.tar.gz',
      'fiber-test.c',
      'fructose-test.c',
      'orange-test.c',
    ]

    for f in data_files:
      file_util.copy(self.data_path(f), tmp_dir)

    filenames = [ orange_builder_script, fructose_builder_script, fiber_builder_script ]
    config = builder_config()
    config.build_root = path.join(tmp_dir, 'BUILD')
    config.no_network = True
    config.source_dir = self.data_dir()
    env = builder_env(config, filenames)
    bldr = builder(env)
    packages_to_build = [ 'orange' ]
    rv = bldr.build_many_scripts(packages_to_build)
    self.assertEqual( bldr.EXIT_CODE_SUCCESS, rv )

if __name__ == '__main__':
  unit_test.main()
