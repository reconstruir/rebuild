#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base import package_descriptor as PD
from rebuild.base import build_system, build_target, package_descriptor, requirement, requirement_list
from bes.common import string_util

class test_package_descriptor(unit_test):

  def test_init(self):
    self.assertEqual( 'foo-1.2.3-1', PD('foo', '1.2.3-1', []).full_name )
    self.assertEqual( 'foo-1.2.3-1', PD('foo', '1.2.3-1', None).full_name )
    self.assertEqual( 'foo-1.2.3-1', PD('foo', '1.2.3-1').full_name )

  def test_full_name(self):
    self.assertEqual( 'foo-1.2.3-1', PD('foo', '1.2.3-1', []).full_name )

  def test_name_is_valid(self):
    self.assertTrue( PD.name_is_valid('foo') )
    self.assertTrue( PD.name_is_valid('foo_bar') )
    self.assertTrue( PD.name_is_valid('foo-bar') )
    self.assertFalse( PD.name_is_valid(None) )
    self.assertFalse( PD.name_is_valid('') )

  TEST_REQUIREMENTS = requirement_list.parse('d1 >= 1.2.3-1 d2 >= 6.6.6-1', default_system_mask = build_system.ALL)
  TEST_PROPS = { 'a': 5, 'b': 66 }

  def test_to_json(self):
    self.maxDiff = None
    expected_json = '''\
{
  "name": "foo", 
  "properties": {},
  "requirements": [ 
    "all: d1 >= 1.2.3-1", 
    "all: d2 >= 6.6.6-1"
  ], 
  "version": "1.2.3-1" 
}'''

    pi = PD('foo', '1.2.3-1', requirements = self.TEST_REQUIREMENTS)
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

    expected_info = PD('foo', '1.2.3-1', requirements = self.TEST_REQUIREMENTS)
    actual_info = PD.parse_json(json)

    self.assertEqual( expected_info, actual_info )

  def test_parse_json_null_requirements(self):
    json = '''\
{
  "version": "1.2.3-1", 
  "name": "foo", 
  "requirements": null
}'''

    expected_info = PD('foo', '1.2.3-1')
    actual_info = PD.parse_json(json)

    self.assertEqual( expected_info, actual_info )

  def test_parse_string(self):
    self.assertEqual( PD('foo', '1.2.3-1'), PD.parse('foo-1.2.3-1') )

  def test_lt(self):
    self.assertTrue( PD('foo', '1.2.3-1') < PD('foo', '1.2.3-2') )
    self.assertTrue( PD('foo', '1.2.3-2') < PD('foo', '1.2.4-1') )
    self.assertTrue( PD('foo', '1.2.3-1') < PD('foo', '1.2.4.5-1') )

  def test_properties_to_string(self):
    self.assertEqual( 'a=5; b=66', PD('foo', '1.2.3-1', properties = self.TEST_PROPS).properties_to_string() )

  def test_str(self):
    self.assertEqual( 'foo-1.2.3-1', str(PD('foo', '1.2.3-1')) )

  def test_str_with_requirements(self):
    self.assertEqual( 'foo-1.2.3-1(d1 >= 1.2.3-1 d2 >= 6.6.6-1)', str(PD('foo', '1.2.3-1', requirements = self.TEST_REQUIREMENTS)) )

  def test_str_with_properties(self):
    self.assertEqual( 'foo-1.2.3-1(a=5; b=66)', str(PD('foo', '1.2.3-1', properties = self.TEST_PROPS)) )

  def test_str_with_requirements_and_properties(self):
    self.assertEqual( 'foo-1.2.3-1(d1 >= 1.2.3-1 d2 >= 6.6.6-1; a=5; b=66)', str(PD('foo', '1.2.3-1', requirements = self.TEST_REQUIREMENTS, properties = self.TEST_PROPS)) )

  def test_parse_requirements(self):
    self.maxDiff = None
    requirements = [
      'all: foo >= 1.2.3-1',
      'all: bar >= 6.6.6-6',
    ]
    expected_requirements = requirement_list.parse('foo(all) >= 1.2.3-1 bar(all) >= 6.6.6-6')
    actual_requirements = PD.parse_requirements(requirements)

    self.assertEqual( expected_requirements, actual_requirements )
    
  def __full_name_cmp(self, s1, s2):
    pi1 = PD.parse(s1)
    p12 = PD.parse(s2)
    return PD.full_name_cmp(pi1, p12)

  def test_full_name_cmp(self):
    self.assertEqual( 0, self.__full_name_cmp('foo-1.2.3-1', 'foo-1.2.3-1') )
    self.assertEqual( 1, self.__full_name_cmp('foo-1.2.4-1', 'foo-1.2.3-1') )
    self.assertEqual( 1, self.__full_name_cmp('foo-1.2.3-2', 'foo-1.2.3-1') )

  def test_tarball_filename(self):
    self.assertEqual( 'foo-1.2.3-1.tar.gz', PD('foo', '1.2.3-1').tarball_filename )

  def test_artifact_path(self):
    self.assertEqual( 'macos/x86_64/release/foo-1.2.3-1.tar.gz', PD('foo', '1.2.3-1').artifact_path(build_target('macos', 'release')) )
    self.assertEqual( 'macos/x86_64/debug/foo-1.2.3-1.tar.gz', PD('foo', '1.2.3-1').artifact_path(build_target('macos', 'debug')) )
    self.assertEqual( 'linux/x86_64/release/foo-1.2.3-1.tar.gz', PD('foo', '1.2.3-1').artifact_path(build_target('linux', 'release')) )
    self.assertEqual( 'linux/x86_64/debug/foo-1.2.3-1.tar.gz', PD('foo', '1.2.3-1').artifact_path(build_target('linux', 'debug')) )

if __name__ == '__main__':
  unit_test.main()
