#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.base import build_system, build_target, requirement
from rebuild.package_manager import package_descriptor
from rebuild.package_manager.package_db_entry import package_db_entry

class test_database_entry(unit_test):

  TEST_REQUIREMENTS = requirement.parse('foo >= 1.2.3-1 bar >= 6.6.6-1', default_system_mask = build_system.ALL)
  TEST_FILES = [ 'f1', 'f2' ]

  def test_str(self):
    e = package_db_entry(package_descriptor('kiwi', '6.7.8-2', requirements = self.TEST_REQUIREMENTS), self.TEST_FILES)
    self.assertEqual( 'kiwi-6.7.8-2(foo >= 1.2.3-1 bar >= 6.6.6-1)[f1, f2]', str(e) )

  def test_to_json(self):
    self.maxDiff = None
    e = package_db_entry(package_descriptor('kiwi', '6.7.8-2', requirements = self.TEST_REQUIREMENTS), self.TEST_FILES)
    expected_json='''\
{
  "files": [
    "f1", 
    "f2"
  ], 
  "info": { 
    "build_requirements": [], 
    "name": "kiwi", 
    "properties": {}, 
    "requirements": [ 
      "all: foo >= 1.2.3-1", 
      "all: bar >= 6.6.6-1" 
    ], 
    "version": "6.7.8-2"
  }
}'''

    self.assert_string_equal_ws( expected_json, e.to_json() )

  def test_parse_json(self):
    json = '''\
{
  "files": [
    "f1", 
    "f2"
  ],
  "info": {
    "build_requirements": [], 
    "version": "6.7.8-2", 
    "name": "kiwi", 
    "requirements": [
      "all: foo >= 1.2.3-1", 
      "all: bar >= 6.6.6-1"
    ] 
  }
}'''
    expected_entry = package_db_entry(package_descriptor('kiwi', '6.7.8-2', requirements = self.TEST_REQUIREMENTS), self.TEST_FILES)
    actual_entry = package_db_entry.parse_json(json)

    self.assertEqual( expected_entry, actual_entry )

if __name__ == '__main__':
  unit_test.main()
