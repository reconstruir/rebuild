#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file
from rebuild.base import build_target, build_version
from rebuild.package_manager import Package
from rebuild.packager.unit_test_packaging import unit_test_packaging
from rebuild.packager import rebuild_builder, rebuild_config, rebuild_env

class test_builder_autoconf(unit_test):

  __unit_test_data_dir__ = 'test_data/packager'
  
  def test_amhello(self):
    self._build_autoconf_package(self, 'amhello', '1.0', '1', self.data_dir())

  def test_water(self):
    self._build_autoconf_package(self, 'water', '1.0.0', '1', self.data_dir())

  def test_mercury(self):
    package = self._build_autoconf_package(self, 'mercury', '2.3.4', '0', self.data_dir())
    expected_files = [
      'bin/mercury_program1',
      'bin/mercury_program2',
      'bin/rebbe_mercury_program1',
      'bin/rebbe_mercury_program2',
      'include/mercury1/mercury1.h',
      'include/mercury2/mercury2.h',
      'lib/libmercury1.a',
      'lib/libmercury2.a',
      'lib/librebbe_mercury1.a',
      'lib/librebbe_mercury2.a',
      'lib/pkgconfig/mercury.pc',
      'lib/pkgconfig/rebbe_mercury.pc',
      'share/doc/mercury/README',
    ]
    self.assertEqual( expected_files, package.files )
    self.assertEqual( 'mercury', package.info.name )
    self.assertEqual( build_version('2.3.4', 0, 0), package.info.version )
    self.assertEqual( 'lib', package.info.properties['category'] )

  def test_arsenic(self):
    package = self._build_autoconf_package(self, 'arsenic', '1.2.9', '0', self.data_dir())
    expected_files = [
      'bin/arsenic_program1',
      'bin/arsenic_program2',
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
    self.assertEqual( expected_files, package.files )
    self.assertEqual( 'arsenic', package.info.name )
    self.assertEqual( build_version('1.2.9', 0, 0), package.info.version )
    self.assertEqual( 'lib', package.info.properties['category'] )

  @classmethod
  def _build_autoconf_package(clazz, asserter, name, version, revision, tarball_dir):
    tmp_dir = temp_file.make_temp_dir()
    build_script_content = unit_test_packaging.make_build_script_content(name, version, revision)
    build_script = file_util.save(path.join(tmp_dir, 'build.py'), content = build_script_content)
    tarball_filename = '%s-%s.tar.gz' % (name, version)
    tarball_path = path.join(tarball_dir, tarball_filename)
    file_util.copy(path.join(tarball_dir, tarball_filename), tmp_dir)
    filenames = [ build_script ]
    bt = build_target()
    config = rebuild_config()
    # FIXME change this to the tarball_dir see if it works remove need for tmp_dir
    config.build_root = path.join(tmp_dir, 'BUILD')
    config.source_dir = tmp_dir
    config.no_network = True
    config.no_checksums = True
    config.verbose = True
    env = rebuild_env(config, filenames)
    builder = rebuild_builder(env, filenames)
    script = env.script_manager.scripts[ name ]
    env.checksum_manager.ignore(script.descriptor.full_name)
    rv = builder.run_build_script(script, env)
    #runner.run_build_script(script, env)
    if not rv.status == rebuild_builder.SCRIPT_SUCCESS:
      print(rv.status)
    asserter.assertEqual( rebuild_builder.SCRIPT_SUCCESS, rv.status )
    tarball = rv.packager_result.output['published_tarball']
    package = Package(tarball)
    return package
    
if __name__ == '__main__':
  unit_test.main()
