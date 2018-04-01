#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.base import build_system, build_target, package_descriptor, requirement as R, requirement_list as RL
from rebuild.package.new_package_db_entry import new_package_db_entry as PE

class test_new_package_db_entry(unit_test):

  TEST_REQUIREMENTS = RL.parse('foo >= 1.2.3-1 bar >= 6.6.6-1', default_system_mask = build_system.ALL)
  TEST_FILES = [ 'f1', 'f2' ]
  TEST_PROPERTIES = { 'p1': 'v1', 'p2': 6 }

  TEST_ENTRY = PE('kiwi-6.7.8-2.tar.gz', '', 'kiwi', '6.7.8-2', 'macos', 'release', 'x86_64', None,
                  TEST_REQUIREMENTS, TEST_PROPERTIES, TEST_FILES)

  def test_descriptor(self):
    self.assertEqual( package_descriptor('kiwi', '6.7.8-2', self.TEST_PROPERTIES, self.TEST_REQUIREMENTS),
                      self.TEST_ENTRY.descriptor )

  def test_build_target(self):
    self.assertEqual( build_target('macos', 'release', [ 'x86_64' ], None), self.TEST_ENTRY.build_target )

  def test_to_json(self):
    self.maxDiff = None
    expected_json = '''\
{
 "_format_version": 2,
 "arch": "x86_64",
 "checksum": "",
 "distro": null,
 "filename": "kiwi-6.7.8-2.tar.gz",
 "files": [ "f1", "f2" ],
 "level": "release",
 "name": "kiwi",
 "properties": { "p1": "v1", "p2": 6 },
 "requirements": [ "foo >= 1.2.3-1", "bar >= 6.6.6-1" ], "system": "macos", "version": "6.7.8-2"
}'''
    self.assert_string_equal_ws( expected_json, self.TEST_ENTRY.to_json() )

  def test_parse_json_v2(self):
    json = '''\
{
 "_format_version": 2,
 "arch": "x86_64",
 "checksum": "",
 "distro": null,
 "filename": "kiwi-6.7.8-2.tar.gz",
 "files": [ "f1", "f2" ],
 "level": "release",
 "name": "kiwi",
 "properties": { "p1": "v1", "p2": 6 },
 "requirements": [ "all: foo >= 1.2.3-1", "all: bar >= 6.6.6-1" ], "system": "macos", "version": "6.7.8-2"
}'''
    actual_entry = PE.parse_json(json)
    self.assertEqual( self.TEST_ENTRY, actual_entry )

  def test_parse_json_v1(self):
    json = '''\
{
  "files": [
    "f1", 
    "f2"
  ],
  "descriptor": {
    "version": "6.7.8-2", 
    "name": "kiwi", 
    "requirements": [
      "all: foo >= 1.2.3-1", 
      "all: bar >= 6.6.6-1"
    ] ,
  "properties": { "p1": "v1", "p2": 6 }
  }
}'''
    expected_entry = PE('', '', 'kiwi', '6.7.8-2', '', '', '', None,
                        self.TEST_REQUIREMENTS, self.TEST_PROPERTIES, self.TEST_FILES)
    actual_entry = PE.parse_json(json)
    self.assertEqual( expected_entry, actual_entry )

if __name__ == '__main__':
  unit_test.main()
