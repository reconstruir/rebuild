#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path
from bes.test import unit_test_helper
from bes.fs import file_util, temp_file
from rebuild import build_target
from rebuild.packager import rebuild_builder
from rebuild.packager.unit_test_packaging import unit_test_packaging

class test_rebuild_builder(unit_test_helper):

  __unit_test_data_dir__ = 'test_data/packager'

  DEBUG = False
  DEBUG = True
  
  def test_amhello(self):
    bt = build_target()
    tmp_dir = temp_file.make_temp_dir()
    amhello_build_script = unit_test_packaging.make_build_script(tmp_dir, 'build_amhello.py', 'amhello', '1.0', 0)
    file_util.copy(self.data_path('amhello-1.0.tar.gz'), tmp_dir)
    filenames = [ amhello_build_script ]
    builder = rebuild_builder(bt, tmp_dir, filenames)
    opts = {}
    packages = [ 'amhello' ]
    builder_config = rebuild_builder.builder_config(False, # keep_going,
                                                    False, # disabled,
                                                    False, # users,
                                                    False, # deps_only,
                                                    False, # skip_to_step,
                                                    False) # tools_only
    rv = builder.build_many_scripts(packages, builder_config, opts)
    self.assertEqual( rebuild_builder.EXIT_CODE_SUCCESS, rv )

  def xxxtest_libpng(self):
    bt = build_target()
    tmp_dir = temp_file.make_temp_dir()
    filenames = [ self.data_path('zlib/build_zlib.py'), self.data_path('libpng/build_libpng.py') ]
    builder = rebuild_builder(bt, tmp_dir, filenames)
    opts = {}
    packages = [ 'zlib', 'libpng' ]
    builder_config = rebuild_builder.builder_config(False, # keep_going,
                                                    False, # disabled,
                                                    False, # users,
                                                    False, # deps_only,
                                                    False, # skip_to_step,
                                                    False) # tools_only
    rv = builder.build_many_scripts(packages, builder_config, opts)
    self.assertEqual( rebuild_builder.EXIT_CODE_SUCCESS, rv )

  def test_fructose(self):
    bt = build_target()
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print "tmp_dir: ", tmp_dir
    data_files = [
      'build_fructose.py',
      'fructose-3.4.5.tar.gz',
      'fructose-test.c',
    ]

    for f in data_files:
      file_util.copy(self.data_path(f), tmp_dir)

    filenames = [ path.join(tmp_dir, 'build_fructose.py') ]
    builder = rebuild_builder(bt, tmp_dir, filenames)
    opts = {}
    packages_to_build = [ 'fructose' ]
    builder_config = rebuild_builder.builder_config(False, # keep_going,
                                                    False, # disabled,
                                                    False, # users,
                                                    False, # deps_only,
                                                    False, # skip_to_step,
                                                    False) # tools_only
    rv = builder.build_many_scripts(packages_to_build, builder_config, opts)
    self.assertEqual( rebuild_builder.EXIT_CODE_SUCCESS, rv )
    
  def xxxtest_orange(self):
    bt = build_target()
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print "tmp_dir: ", tmp_dir
    orange_requirements = [
      'all: fructose >= 3.4.5-6',
      'all: fiber >= 1.0.0-0',
    ]
    orange_build_script = unit_test_packaging.make_build_script(tmp_dir, 'build_orange.py', 'orange', '6.5.4', 3,
                                                                requirements = orange_requirements,
                                                                tests = [ 'all: orange-test.c' ])
    fructose_build_script = unit_test_packaging.make_build_script(tmp_dir, 'build_fructose.py', 'fructose', '3.4.5', 6,
                                                                  tests = [ 'all: fructose-test.c' ])
    fiber_build_script = unit_test_packaging.make_build_script(tmp_dir, 'build_fiber.py', 'fiber', '1.0.0', 0,
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

    filenames = [ orange_build_script, fructose_build_script, fiber_build_script ]
    builder = rebuild_builder(bt, tmp_dir, filenames)
    opts = {}
    packages_to_build = [ 'orange' ]
    builder_config = rebuild_builder.builder_config(False, # keep_going,
                                                         False, # disabled,
                                                         False, # users,
                                                         False, # deps_only,
                                                         False, # skip_to_step,
                                                         False) # tools_only
    rv = builder.build_many_scripts(packages_to_build, builder_config, opts)
    self.assertEqual( rebuild_builder.EXIT_CODE_SUCCESS, rv )
    
if __name__ == '__main__':
  unit_test_helper.main()
