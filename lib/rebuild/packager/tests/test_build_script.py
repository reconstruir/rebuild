#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest
from bes.fs import temp_file
from rebuild import package_descriptor
from rebuild.base import build_category, build_target, requirement
from rebuild.packager import build_script, rebuild_config, rebuild_env

class test_build_script(unittest.TestCase):

  TEST_DATA_DIR = path.abspath(path.join(path.dirname(__file__), 'test_data/build_script'))

  def test_zlib(self):
    filename = path.join(self.TEST_DATA_DIR, 'build_zlib.py')
    script = self._load_build_script(filename)
    expected_requirements = []
    expected_properties = { package_descriptor.PROPERTY_CATEGORY: build_category.LIB }
    self.assertEqual( package_descriptor('zlib', '1.2.8-1', requirements = expected_requirements, properties = expected_properties), script.descriptor )
    self.assertEqual( [], script.descriptor.requirements )
    self.assertEqual( [], script.descriptor.build_requirements )

  def test_libjpeg(self):
    filename = path.join(self.TEST_DATA_DIR, 'build_libjpeg.py')
    script = self._load_build_script(filename)
    expected_requirements = []
    expected_properties = { package_descriptor.PROPERTY_CATEGORY: build_category.LIB }
    self.assertEqual( package_descriptor('libjpeg', '9a-1', requirements = expected_requirements, properties = expected_properties), script.descriptor )
    self.assertEqual( [], script.descriptor.requirements )
    self.assertEqual( [], script.descriptor.build_requirements )

  def test_libopenjpeg(self):
    filename = path.join(self.TEST_DATA_DIR, 'build_libopenjpeg.py')
    script = self._load_build_script(filename)

    expected_requirements = []
    expected_properties = { package_descriptor.PROPERTY_CATEGORY: build_category.LIB }
    expected_build_requirements = [] #requirement.parse('cmake(all) >= 3.3.1-1')
    expected_package_info = package_descriptor('libopenjpeg', '2.1-1',
                                               requirements = expected_requirements,
                                               build_requirements = expected_build_requirements,
                                               properties = expected_properties)
    self.assertEqual( expected_package_info, script.descriptor )
    self.assertEqual( expected_requirements, script.descriptor.requirements )
    self.assertEqual( expected_build_requirements, script.descriptor.build_requirements )

  def test_libpng(self):
    filename = path.join(self.TEST_DATA_DIR, 'build_libpng.py')
    script = self._load_build_script(filename)

    expected_requirements = [] #requirement.parse('zlib(all) >= 1.2.8-1')
    expected_properties = { package_descriptor.PROPERTY_CATEGORY: build_category.LIB }
    expected_build_requirements = []
    expected_package_info = package_descriptor('libpng', '1.6.18-1',
                                               requirements = expected_requirements,
                                               properties = expected_properties)

    self.assertEqual( expected_package_info, script.descriptor )
    self.assertEqual( expected_requirements, script.descriptor.requirements )
    self.assertEqual( expected_build_requirements, script.descriptor.build_requirements )
    self.assertEqual( build_category.LIB, script.descriptor.properties[package_descriptor.PROPERTY_CATEGORY] )

  def _load_build_script(self, filename):
    bt = build_target()
    config = rebuild_config()
    config.build_root = temp_file.make_temp_dir()
    config.no_network = True
    config.no_checksums = True
    config.source_dir = path.dirname(filename)
    config.verbose = True
    env = rebuild_env(config, [ filename ])
    scripts = build_script.load_build_scripts(filename, env)
    self.assertEqual( 1, len(scripts) )
    return scripts[0]
    
if __name__ == '__main__':
  unittest.main()
