#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path
from bes.testing.unit_test import unit_test
from bes.sqlite import sqlite
from rebuild.base import build_system, build_target, package_descriptor, requirement as R, requirement_list as RL
from rebuild.package.new_package_db_entry import new_package_db_entry as PE
from rebuild.package.new_package_db import new_package_db as DB

class test_new_package_db_entry(unit_test):

  TEST_REQUIREMENTS = RL.parse('foo >= 1.2.3-1 bar >= 6.6.6-1')
  TEST_FILES = [ 'f1', 'f2' ]
  TEST_PROPERTIES = { 'p1': 'v1', 'p2': 6 }

  TEST_ENTRY = PE('kiwi', '6.7.8', 2, 0, TEST_REQUIREMENTS, TEST_PROPERTIES, TEST_FILES)

  def test_descriptor(self):
    self.assertEqual( package_descriptor('kiwi', '6.7.8-2', self.TEST_PROPERTIES, self.TEST_REQUIREMENTS),
                      self.TEST_ENTRY.descriptor )

  def test_to_json(self):
    self.maxDiff = None
    expected_json = '''\
{
  "_format_version": 2, 
  "epoch": 0, 
  "files": [
    "f1", 
    "f2"
  ], 
  "name": "kiwi", 
  "properties": {
    "p1": "v1", 
    "p2": 6
  }, 
  "requirements": [
    "foo >= 1.2.3-1", 
    "bar >= 6.6.6-1"
  ], 
  "revision": 2, 
  "version": "6.7.8"
}'''
    self.assertMultiLineEqual( expected_json, self.TEST_ENTRY.to_json() )

  def test_parse_json_v2(self):
    json = '''\
{
  "_format_version": 2, 
  "epoch": 0, 
  "files": [
    "f1", 
    "f2"
  ], 
  "name": "kiwi", 
  "properties": {
    "p1": "v1", 
    "p2": 6
  }, 
  "requirements": [
    "foo >= 1.2.3-1", 
    "bar >= 6.6.6-1"
  ], 
  "revision": 2, 
  "version": "6.7.8"
}'''
    actual_entry = PE.parse_json(json)
    self.maxDiff = None
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
      "foo >= 1.2.3-1", 
      "bar >= 6.6.6-1"
    ] ,
  "properties": { "p1": "v1", "p2": 6 }
  }
}'''
    expected_entry = PE('kiwi', '6.7.8', 2, 0, self.TEST_REQUIREMENTS, self.TEST_PROPERTIES, self.TEST_FILES)
    actual_entry = PE.parse_json(json)
    self.assertEqual( expected_entry, actual_entry )

  def test_to_simple_dict(self):
    expected = {
      '_format_version': 2, 
      'epoch': 0, 
      'files': [ 'f1',  'f2' ], 
      'name': 'kiwi', 
      'properties': { 'p1': 'v1',  'p2': 6 }, 
      'requirements': [ 'foo >= 1.2.3-1',  'bar >= 6.6.6-1' ], 
      'revision': 2, 
      'version': '6.7.8',
    }
    self.assertEqual( expected, self.TEST_ENTRY.to_simple_dict() )
    
  def test_to_sql_dict(self):
    expected = {
      'epoch': '0',
      'files': '\'["f1", "f2"]\'',
      'name': '\'kiwi\'', 
      'properties': '\'{"p2": 6, "p1": "v1"}\'',
      'requirements': '\'["foo >= 1.2.3-1", "bar >= 6.6.6-1"]\'',
      'revision': '2',
      'version': '\'6.7.8\'',
    }
    self.assertEqual( expected, self.TEST_ENTRY.to_sql_dict() )

  def test_from_sql_row(self):
    db = sqlite(':memory:')
    db.execute(DB.SCHEMA_PACKAGES)
    d = self.TEST_ENTRY.to_sql_dict()
    keys = ', '.join(d.keys())
    values = ', '.join(d.values())
    sql = 'INSERT INTO packages(%s) values(%s)' % (keys, values)
    db.execute(sql)
    db.commit()
    rows = db.select_namedtuples('SELECT * FROM packages')
    self.assertEqual( 1, len(rows) )
    self.assertEqual( self.TEST_ENTRY, PE.from_sql_row(rows[0]) )
    
if __name__ == '__main__':
  unit_test.main()
