#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.unit_test import unit_test
from rebuild import build_target, package_descriptor, requirement, System
from bes.common import string_util

class test_package_info(unit_test):

  def test_init(self):
    self.assertEqual( 'foo-1.2.3-1', package_descriptor('foo', '1.2.3-1', []).full_name )
    self.assertEqual( 'foo-1.2.3-1', package_descriptor('foo', '1.2.3-1', None).full_name )
    self.assertEqual( 'foo-1.2.3-1', package_descriptor('foo', '1.2.3-1').full_name )

  def test_full_name(self):
    self.assertEqual( 'foo-1.2.3-1', package_descriptor('foo', '1.2.3-1', []).full_name )

  def test_name_is_valid(self):
    self.assertTrue( package_descriptor.name_is_valid('foo') )
    self.assertTrue( package_descriptor.name_is_valid('foo_bar') )
    self.assertTrue( package_descriptor.name_is_valid('foo-bar') )
    self.assertFalse( package_descriptor.name_is_valid(None) )
    self.assertFalse( package_descriptor.name_is_valid('') )

  TEST_REQUIREMENTS = requirement.parse('d1 >= 1.2.3-1 d2 >= 6.6.6-1', default_system_mask = System.ALL)
  TEST_PROPS = { 'a': 5, 'b': 66 }

  def test_to_json(self):
    self.maxDiff = None
    expected_json = '''\
{
  "build_requirements": [], 
  "name": "foo", 
  "properties": {},
  "requirements": [ 
    "all: d1 >= 1.2.3-1", 
    "all: d2 >= 6.6.6-1"
  ], 
  "version": "1.2.3-1" 
}'''

    pi = package_descriptor('foo', '1.2.3-1', self.TEST_REQUIREMENTS)
    actual_json = pi.to_json()

    self.assert_string_equal_ws( expected_json, actual_json )

  def test_parse_json(self):
    json = '''\
{
  "version": "1.2.3-1", 
  "name": "foo", 
  "requirements": [
    "all: d1 >= 1.2.3-1", 
    "all: d2 >= 6.6.6-1"
  ]
}'''

    expected_info = package_descriptor('foo', '1.2.3-1', self.TEST_REQUIREMENTS)
    actual_info = package_descriptor.parse_json(json)

    self.assertEqual( expected_info, actual_info )

  def test_parse_json_null_requirements(self):
    json = '''\
{
  "version": "1.2.3-1", 
  "name": "foo", 
  "requirements": null
}'''

    expected_info = package_descriptor('foo', '1.2.3-1', None)
    actual_info = package_descriptor.parse_json(json)

    self.assertEqual( expected_info, actual_info )

  def test_parse_string(self):
    self.assertEqual( package_descriptor('foo', '1.2.3-1'), package_descriptor.parse('foo-1.2.3-1') )

  def test_lt(self):
    self.assertTrue( package_descriptor('foo', '1.2.3-1') < package_descriptor('foo', '1.2.3-2') )
    self.assertTrue( package_descriptor('foo', '1.2.3-2') < package_descriptor('foo', '1.2.4-1') )
    self.assertTrue( package_descriptor('foo', '1.2.3-1') < package_descriptor('foo', '1.2.4.5-1') )

  def test_properties_to_string(self):
    self.assertEqual( 'a=5; b=66', package_descriptor('foo', '1.2.3-1', properties = self.TEST_PROPS).properties_to_string() )

  def test_str(self):
    self.assertEqual( 'foo-1.2.3-1', str(package_descriptor('foo', '1.2.3-1')) )

  def test_str_with_requirements(self):
    self.assertEqual( 'foo-1.2.3-1(d1 >= 1.2.3-1 d2 >= 6.6.6-1)', str(package_descriptor('foo', '1.2.3-1', requirements = self.TEST_REQUIREMENTS)) )

  def test_str_with_properties(self):
    self.assertEqual( 'foo-1.2.3-1(a=5; b=66)', str(package_descriptor('foo', '1.2.3-1', properties = self.TEST_PROPS)) )

  def test_str_with_requirements_and_properties(self):
    self.assertEqual( 'foo-1.2.3-1(d1 >= 1.2.3-1 d2 >= 6.6.6-1; a=5; b=66)', str(package_descriptor('foo', '1.2.3-1', requirements = self.TEST_REQUIREMENTS, properties = self.TEST_PROPS)) )

  def test_parse_requirements(self):
    self.maxDiff = None
    requirements = [
      'all: foo >= 1.2.3-1',
      'all: bar >= 6.6.6-6',
    ]
    expected_requirements = requirement.parse('foo(all) >= 1.2.3-1 bar(all) >= 6.6.6-6')
    actual_requirements = package_descriptor.parse_requirements(requirements)

    self.assertEqual( expected_requirements, actual_requirements )

###  def test_parse_requirements_with_build_target(self):
###    requirements = [
###      'android: foo >= 1.2.3-1',
###      'ios: bar >= 6.6.6-6',
###    ]
###    expected_ios_requirements = [
###      package_descriptor('bar', '6.6.6-6'),
###    ]
###
###    # android
###    expected_android_requirements = [
###      package_descriptor('foo', '1.2.3-1'),
###    ]
###    android_build_target = build_target(System.ANDROID)
###    android_actual_requirements = package_descriptor.parse_requirements(requirements, build_target = android_build_target)
###    self.assertEqual( expected_android_requirements, android_actual_requirements )
###
###    # ios
###    expected_ios_requirements = [
###      package_descriptor('bar', '6.6.6-6'),
###    ]
###    ios_build_target = build_target(System.IOS)
###    ios_actual_requirements = package_descriptor.parse_requirements(requirements, build_target = ios_build_target)
###    self.assertEqual( expected_ios_requirements, ios_actual_requirements )
    
  def __full_name_cmp(self, s1, s2):
    pi1 = package_descriptor.parse(s1)
    p12 = package_descriptor.parse(s2)
    return package_descriptor.full_name_cmp(pi1, p12)

  def test_full_name_cmp(self):
    self.assertEqual( 0, self.__full_name_cmp('foo-1.2.3-1', 'foo-1.2.3-1') )
    self.assertEqual( 1, self.__full_name_cmp('foo-1.2.4-1', 'foo-1.2.3-1') )
    self.assertEqual( 1, self.__full_name_cmp('foo-1.2.3-2', 'foo-1.2.3-1') )

  def test_tarball_filename(self):
    self.assertEqual( 'foo-1.2.3-1.tar.gz', package_descriptor('foo', '1.2.3-1').tarball_filename )

  def test_artifact_path(self):
    self.assertEqual( 'macos/release/foo-1.2.3-1.tar.gz', package_descriptor('foo', '1.2.3-1').artifact_path(build_target('macos', 'release')) )
    self.assertEqual( 'macos/debug/foo-1.2.3-1.tar.gz', package_descriptor('foo', '1.2.3-1').artifact_path(build_target('macos', 'debug')) )
    self.assertEqual( 'linux/release/foo-1.2.3-1.tar.gz', package_descriptor('foo', '1.2.3-1').artifact_path(build_target('linux', 'release')) )
    self.assertEqual( 'linux/debug/foo-1.2.3-1.tar.gz', package_descriptor('foo', '1.2.3-1').artifact_path(build_target('linux', 'debug')) )

if __name__ == '__main__':
  unit_test.main()
