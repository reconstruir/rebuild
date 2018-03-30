#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from collections import namedtuple
import os.path as path
from bes.fs import file_util, temp_file
from bes.git import git_download_cache
from bes.testing.unit_test import unit_test
from rebuild.builder import builder, builder_config, builder_env
from rebuild.builder.unit_test_packaging import unit_test_packaging
from rebuild.checksum import checksum_manager
from rebuild.package import artifact_manager, package_manager
from rebuild.source_finder import local_source_finder, source_finder_chain
from rebuild.base import build_arch, build_level, build_system, build_target, package_descriptor

class test_builder(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/packager'

  DEBUG = False
  #DEBUG = True

  def test_amhello(self):
    tmp_dir = temp_file.make_temp_dir()
    amhello_builder_script = unit_test_packaging.make_recipe(1, tmp_dir, 'build_amhello.py', 'amhello', '1.0', 0)
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
    self.assertEqual( builder.EXIT_CODE_SUCCESS, rv )

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
    self.assertEqual( builder.EXIT_CODE_SUCCESS, rv )

  def test_fructose(self):
    rv = self._build_project([
      'build_fructose.rebc',
      'fructose-3.4.5.tar.gz',
      'fructose-test.c',
    ], [
      'build_fructose.rebc',
    ], [
      'fructose',
    ])
    self.assertEqual( builder.EXIT_CODE_SUCCESS, rv.exit_code )

  def test_fructose_with_env_vars(self):
    rv = self._build_project([
      'build_fructose_with_env_vars.rebc',
      'fructose-3.4.5.tar.gz',
      'fructose-test.c',
    ], [
      'build_fructose_with_env_vars.rebc',
    ], [
      'fructose',
    ])
    self.assertEqual( builder.EXIT_CODE_SUCCESS, rv.exit_code )
    publish_dir = path.join(rv.tmp_dir, 'BUILD/artifacts')
    self.assertTrue( path.exists(publish_dir) )
    am = artifact_manager(publish_dir, address = None, no_git = True)
    pm = self._make_test_pm(am)
    pdesc = package_descriptor('fructose', '3.4.5-6')
    bt = build_target(system = build_system.HOST,
                      level = build_level.RELEASE,
                      archs = build_arch.HOST_ARCH)
    install_rv = pm.install_package(pdesc, bt, ['BUILD', 'RUN'])
    self.assertTrue( install_rv )
    self.assertEqual( [ 'fructose-3.4.5-6' ], pm.list_all(include_version = True) )
    self.assertEqual( { 'FRUCTOSE_FOO': '666' }, pm.env_vars([ 'fructose' ]) )
    
  def _make_test_pm(self, am):
    root_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    pm_dir = path.join(root_dir, 'package_manager')
    return package_manager(pm_dir, am)

  _build_result = namedtuple('build_result', 'exit_code,tmp_dir')
    
  def _build_project(self, data_files, build_scripts, packages_to_build):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print("tmp_dir: ", tmp_dir)
    for f in data_files:
      file_util.copy(self.data_path(f), tmp_dir)
    filenames = [ path.join(tmp_dir, script) for script in build_scripts ]
    config = builder_config()
    config.build_root = path.join(tmp_dir, 'BUILD')
    config.no_network = True
    config.source_dir = self.data_dir()
    env = builder_env(config, filenames)
    bldr = builder(env)
    exit_code = bldr.build_many_scripts(packages_to_build)
    return self._build_result(exit_code, tmp_dir)
    
if __name__ == '__main__':
  unit_test.main()
