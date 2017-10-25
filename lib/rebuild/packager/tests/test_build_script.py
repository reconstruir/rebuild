#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest
from rebuild import build_target, Category, package_descriptor, requirement
from rebuild.packager import build_script

class test_build_script(unittest.TestCase):

  TEST_DATA_DIR = path.abspath(path.join(path.dirname(__file__), 'test_data/build_script'))

  def test_zlib(self):
    filename = path.join(self.TEST_DATA_DIR, 'build_zlib.py')
    script = build_script.load_build_scripts(filename, build_target())[0]
    expected_requirements = []
    expected_properties = { package_descriptor.PROPERTY_CATEGORY: Category.LIB }
    self.assertEqual( package_descriptor('zlib', '1.2.8-1', requirements = expected_requirements, properties = expected_properties), script.package_descriptor )
    self.assertEqual( [], script.package_descriptor.requirements )
    self.assertEqual( [], script.package_descriptor.build_requirements )

  def test_libjpeg(self):
    filename = path.join(self.TEST_DATA_DIR, 'build_libjpeg.py')
    script = build_script.load_build_scripts(filename, build_target())[0]
    expected_requirements = []
    expected_properties = { package_descriptor.PROPERTY_CATEGORY: Category.LIB }
    self.assertEqual( package_descriptor('libjpeg', '9a-1', requirements = expected_requirements, properties = expected_properties), script.package_descriptor )
    self.assertEqual( [], script.package_descriptor.requirements )
    self.assertEqual( [], script.package_descriptor.build_requirements )

  def test_libopenjpeg(self):
    filename = path.join(self.TEST_DATA_DIR, 'build_libopenjpeg.py')
    script = build_script.load_build_scripts(filename, build_target())[0]

    expected_requirements = []
    expected_properties = { package_descriptor.PROPERTY_CATEGORY: Category.LIB }
    expected_build_requirements = requirement.parse('cmake(all) >= 3.3.1-1')
    expected_package_info = package_descriptor('libopenjpeg', '2.1-1',
                                               requirements = expected_requirements,
                                               build_requirements = expected_build_requirements,
                                               properties = expected_properties)
    self.assertEqual( expected_package_info, script.package_descriptor )
    self.assertEqual( expected_requirements, script.package_descriptor.requirements )
    self.assertEqual( expected_build_requirements, script.package_descriptor.build_requirements )

  def test_libpng(self):
    filename = path.join(self.TEST_DATA_DIR, 'build_libpng.py')
    script = build_script.load_build_scripts(filename, build_target())[0]

    expected_requirements = requirement.parse('zlib(all) >= 1.2.8-1')
    expected_properties = { package_descriptor.PROPERTY_CATEGORY: Category.LIB }
    expected_build_requirements = []
    expected_package_info = package_descriptor('libpng', '1.6.18-1',
                                               requirements = expected_requirements,
                                               properties = expected_properties)

    self.assertEqual( expected_package_info, script.package_descriptor )
    self.assertEqual( expected_requirements, script.package_descriptor.requirements )
    self.assertEqual( expected_build_requirements, script.package_descriptor.build_requirements )
    self.assertEqual( Category.LIB, script.package_descriptor.properties[package_descriptor.PROPERTY_CATEGORY] )

if __name__ == '__main__':
  unittest.main()
