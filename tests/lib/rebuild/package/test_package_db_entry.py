#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
import os.path as path
from bes.testing.unit_test import unit_test
from bes.sqlite import sqlite
from rebuild.base import build_system, build_target, package_descriptor, requirement as R, requirement_list as RL
from rebuild.package.package_db_entry import package_db_entry as PE
from rebuild.package.package_db import package_db as DB
from rebuild.package import package_manifest
from rebuild.package.package_file_list import package_file_list as FCL

class test_package_db_entry(unit_test):

  TEST_REQUIREMENTS = RL.parse('foo >= 1.2.3-1 bar >= 6.6.6-1')
  TEST_FILES = package_manifest(FCL(
    [
      ( 'f1', 'fchk1', 0 ),
      ( 'f2', 'fchk2', 0 ),
    ]),
    FCL([
      ( 'e1', 'echk1', 0 ),
      ( 'e2', 'echk2', 0 ),
    ]),
    'contents_chk')
  TEST_PROPERTIES = { 'p1': 'v1', 'p2': 6 }

  TEST_ENTRY = PE('kiwi', '6.7.8', 2, 0, TEST_REQUIREMENTS, TEST_PROPERTIES, TEST_FILES)

  def test_descriptor(self):
    self.assertEqual( package_descriptor('kiwi', '6.7.8-2', requirements = self.TEST_REQUIREMENTS, properties = self.TEST_PROPERTIES),
                      self.TEST_ENTRY.descriptor )

  def test_to_json(self):
    self.maxDiff = None
    expected_json = '''\
{
  "_format_version": 2, 
  "epoch": 0, 
  "manifest": {
    "contents_checksum": "contents_chk", 
    "env_files": [
      [
        "e1", 
        "echk1", 
        false
      ], 
      [
        "e2", 
        "echk2", 
        false
      ]
    ], 
    "files": [
      [
        "f1", 
        "fchk1", 
        false
      ], 
      [
        "f2", 
        "fchk2", 
        false
      ]
    ]
  }, 
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
  "manifest": {
    "contents_checksum": "contents_chk", 
    "env_files": [
      [
        "e1", 
        "echk1", 
        false
      ], 
      [
        "e2", 
        "echk2", 
        false
      ]
    ], 
    "files": [
      [
        "f1", 
        "fchk1", 
        false
      ], 
      [
        "f2", 
        "fchk2", 
        false
      ]
    ]
  }, 
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

  def test_to_simple_dict(self):
    expected = {
      '_format_version': 2, 
      'epoch': 0,
      'manifest': {
        'env_files': [['e1', 'echk1', False], ['e2', 'echk2', False]],
        'files': [['f1', 'fchk1', False], ['f2', 'fchk2', False]],
        'contents_checksum': 'contents_chk'
      },
      'name': 'kiwi', 
      'properties': { 'p1': 'v1',  'p2': 6 }, 
      'requirements': [ 'foo >= 1.2.3-1',  'bar >= 6.6.6-1' ], 
      'revision': 2, 
      'version': '6.7.8',
    }
    self.assertEqual( expected, self.TEST_ENTRY.to_simple_dict() )

'''    
  def test_to_sql_dict(self):
    expected = {
      'checksum': '\'b6e239213b95578407799e95174bbd47330b9a8c\'',
      'epoch': '0',
      'name': '\'kiwi\'', 
      'properties': '\'{"p1": "v1", "p2": 6}\'',
      'requirements': '\'["foo >= 1.2.3-1", "bar >= 6.6.6-1"]\'',
      'revision': '2',
      'version': '\'6.7.8\'',
    }
    self.assertEqual( expected, self.TEST_ENTRY.to_sql_dict() )
'''

if __name__ == '__main__':
  unit_test.main()
