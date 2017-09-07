#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path
from bes.unit_test import unit_test
from rebuild import build_target, package_descriptor, requirement, System
from rebuild.package_manager.DatabaseEntry import DatabaseEntry

class test_database_entry(unit_test):

  TEST_REQUIREMENTS = requirement.parse('foo >= 1.2.3-1 bar >= 6.6.6-1', default_system_mask = System.ALL)
  TEST_FILES = [ 'f1', 'f2' ]

  def test_str(self):
    e = DatabaseEntry(package_descriptor('kiwi', '6.7.8-2', requirements = self.TEST_REQUIREMENTS), self.TEST_FILES)
    self.assertEqual( 'kiwi-6.7.8-2(foo >= 1.2.3-1 bar >= 6.6.6-1)[f1, f2]', str(e) )

  def test_to_json(self):
    self.maxDiff = None
    e = DatabaseEntry(package_descriptor('kiwi', '6.7.8-2', requirements = self.TEST_REQUIREMENTS), self.TEST_FILES)
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
    expected_entry = DatabaseEntry(package_descriptor('kiwi', '6.7.8-2', requirements = self.TEST_REQUIREMENTS), self.TEST_FILES)
    actual_entry = DatabaseEntry.parse_json(json)

    self.assertEqual( expected_entry, actual_entry )

if __name__ == '__main__':
  unit_test.main()
