#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file
from rebuild.base import build_target, build_version
from rebuild.package import package
from rebuild.builder.unit_test_packaging import unit_test_packaging
from rebuild.builder import builder, builder_config, builder_env

class test_builder_autoconf(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/packager'
  
  def test_amhello(self):
    self._build_autoconf_package(self, 'amhello', '1.0', '1', self.data_dir())

  def test_template(self):
    self._build_autoconf_package(self, 'template', '1.0.0', '1', self.data_dir())

  def test_mercury(self):
    self.maxDiff = None
    pkg = self._build_autoconf_package(self, 'mercury', '1.2.8', '0', self.data_dir())
    expected_files = [
      'bin/mercury_print_env',
      'bin/mercury_program1',
      'bin/mercury_program2',
      'bin/rebbe_mercury_print_env',
      'bin/rebbe_mercury_program1',
      'bin/rebbe_mercury_program2',
      'include/mercury1/mercury1.h',
      'include/mercury2/mercury2.h',
      'lib/libmercury1.a',
      'lib/libmercury2.a',
      'lib/librebbe_mercury1.a',
      'lib/librebbe_mercury2.a',
      'lib/pkgconfig/libmercury1.pc',
      'lib/pkgconfig/libmercury2.pc',
      'lib/pkgconfig/librebbe_mercury1.pc',
      'lib/pkgconfig/librebbe_mercury2.pc',
      'lib/pkgconfig/mercury.pc',
      'lib/pkgconfig/rebbe_mercury.pc',
      'share/doc/mercury/README',
    ]
    self.assertEqual( expected_files, pkg.files )
    self.assertEqual( 'mercury', pkg.info.name )
    self.assertEqual( build_version('1.2.8', 0, 0), pkg.info.version )
    self.assertEqual( 'lib', pkg.info.properties['category'] )

  def test_arsenic(self):
    pkg = self._build_autoconf_package(self, 'arsenic', '1.2.9', '0', self.data_dir())
    expected_files = [
      'bin/arsenic_print_env',
      'bin/arsenic_program1',
      'bin/arsenic_program2',
      'bin/rebbe_arsenic_print_env',
      'bin/rebbe_arsenic_program1',
      'bin/rebbe_arsenic_program2',
      'include/arsenic1/arsenic1.h',
      'include/arsenic2/arsenic2.h',
      'lib/libarsenic1.a',
      'lib/libarsenic2.a',
      'lib/librebbe_arsenic1.a',
      'lib/librebbe_arsenic2.a',
      'lib/pkgconfig/arsenic.pc',
      'lib/pkgconfig/libarsenic1.pc',
      'lib/pkgconfig/libarsenic2.pc',
      'lib/pkgconfig/librebbe_arsenic1.pc',
      'lib/pkgconfig/librebbe_arsenic2.pc',
      'lib/pkgconfig/rebbe_arsenic.pc',
      'share/doc/arsenic/README',
    ]
    self.assertEqual( expected_files, pkg.files )
    self.assertEqual( 'arsenic', pkg.info.name )
    self.assertEqual( build_version('1.2.9', 0, 0), pkg.info.version )
    self.assertEqual( 'lib', pkg.info.properties['category'] )

  @classmethod
  def _build_autoconf_package(clazz, asserter, name, version, revision, tarball_dir):
    tmp_dir = temp_file.make_temp_dir()
    builder_script_content = unit_test_packaging.make_recipe_v1_content(name, version, revision)
    builder_script = file_util.save(path.join(tmp_dir, 'build.py'), content = builder_script_content)
    tarball_filename = '%s-%s.tar.gz' % (name, version)
    tarball_path = path.join(tarball_dir, tarball_filename)
    file_util.copy(path.join(tarball_dir, tarball_filename), tmp_dir)
    filenames = [ builder_script ]
    bt = build_target()
    config = builder_config()
    # FIXME change this to the tarball_dir see if it works remove need for tmp_dir
    config.build_root = path.join(tmp_dir, 'BUILD')
    config.source_dir = tmp_dir
    config.no_network = True
    config.no_checksums = True
    config.verbose = True
    env = builder_env(config, filenames)
    bldr = builder(env)
    script = env.script_manager.scripts[ name ]
    env.checksum_manager.ignore(script.descriptor.full_name)
    rv = bldr.build_script(script, env)
    if not rv.status == bldr.SCRIPT_SUCCESS:
      print(rv.packager_result.message)
    asserter.assertEqual( bldr.SCRIPT_SUCCESS, rv.status )
    tarball = rv.packager_result.output['published_tarball']
    pkg = package(tarball)
    return pkg
    
if __name__ == '__main__':
  unit_test.main()
