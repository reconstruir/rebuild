#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path
from bes.sqlite import sqlite
from bes.testing.unit_test import unit_test
from bes.fs import file_checksum_list
from rebuild.base import build_system, build_target, package_descriptor, requirement_list as RL
from rebuild.package.package_metadata import package_metadata as PM
from rebuild.package.artifact_db import artifact_db as DB

class test_package_metadata(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/lib/rebuild/package'

  TEST_REQUIREMENTS = RL.parse('foo >= 1.2.3-1 bar >= 6.6.6-1')
  TEST_FILES = file_checksum_list([
    ( 'f1', 'chk1' ),
    ( 'f2', 'chk2' ),
  ])
  TEST_PROPERTIES = { 'p1': 'v1', 'p2': 6 }

  TEST_ENTRY = PM('kiwi-6.7.8-2.tar.gz', 'kiwi', '6.7.8', 2, 0, 'macos', 'release', [ 'x86_64' ], None,
                  TEST_REQUIREMENTS, TEST_PROPERTIES, TEST_FILES, 'chk')

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
  "archs": [
    "x86_64"
  ], 
  "checksum": "chk", 
  "distro": null, 
  "epoch": 0, 
  "filename": "kiwi-6.7.8-2.tar.gz", 
  "files": [
    [
      "f1", 
      "chk1"
    ], 
    [
      "f2", 
      "chk2"
    ]
  ], 
  "level": "release", 
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
  "system": "macos", 
  "version": "6.7.8"
}'''
    self.assertMultiLineEqual( expected_json, self.TEST_ENTRY.to_json() )

  def test_parse_json_v2(self):
    json = '''\
{
  "_format_version": 2, 
  "archs": [
    "x86_64"
  ], 
  "checksum": "chk", 
  "distro": null, 
  "epoch": 0, 
  "filename": "kiwi-6.7.8-2.tar.gz", 
  "files": [
    [
      "f1", 
      "chk1"
    ], 
    [
      "f2", 
      "chk2"
    ]
  ], 
  "level": "release", 
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
  "system": "macos", 
  "version": "6.7.8"
}'''
    actual_entry = PM.parse_json(json)
    self.maxDiff = None
    self.assertEqual( self.TEST_ENTRY, actual_entry )

  def test_parse_json_v1(self):
    json = '''\
{
  "requirements": [
    "foo >= 1.2.3-1", 
    "bar >= 6.6.6-1"
  ], 
  "name": "kiwi", 
  "level": "release", 
  "system": "macos", 
  "version": "6.7.8-2", 
  "properties": {
    "p1": "v1",
    "p2": 6
  }, 
  "archs": [
    "x86_64"
  ], 
  "distro": null
}
'''
    expected_entry = PM('', 'kiwi', '6.7.8', 2, 0, 'macos', 'release', [ 'x86_64' ], None,
                        self.TEST_REQUIREMENTS, self.TEST_PROPERTIES, None, '')
    actual_entry = PM.parse_json(json)
    self.assertEqual( expected_entry, actual_entry )

  def test_to_sql_dict(self):
    expected = {
      'properties': '\'{"p1": "v1", "p2": 6}\'',
      'requirements': '\'["foo >= 1.2.3-1", "bar >= 6.6.6-1"]\'',
      'name': "'kiwi'",
      'level': "'release'",
      'checksum': "'chk'",
      'system': "'macos'",
      'filename': "'kiwi-6.7.8-2.tar.gz'",
      'epoch': '0',
      'version': "'6.7.8'",
      'revision': '2',
      'archs': '\'["x86_64"]\'',
      'distro': "''"
    }
    self.assertEqual( expected, self.TEST_ENTRY.to_sql_dict() )

  def test_from_sql_row(self):
    db = sqlite(':memory:')
    db.execute(DB.SCHEMA_ARTIFACTS)
    d = self.TEST_ENTRY.to_sql_dict()
    keys = ', '.join(d.keys())
    values = ', '.join(d.values())
    db.execute('''INSERT INTO artifacts (%s) values (%s)''' % (keys, values))
    db.execute('''CREATE TABLE kiwi_files (filename TEXT PRIMARY KEY NOT NULL, checksum TEXT);''')
    db.execute('''INSERT INTO kiwi_files (filename, checksum) values ('f1', 'chk1');''')
    db.execute('''INSERT INTO kiwi_files (filename, checksum) values ('f2', 'chk2');''')
    db.commit()
    rows = db.select_namedtuples("""SELECT * FROM artifacts where name='kiwi'""")
    files_rows = db.select_namedtuples('SELECT * FROM kiwi_files')
    self.assertEqual( 1, len(rows) )
    self.assertEqual( 2, len(files_rows) )
    self.assertEqual( self.TEST_ENTRY, PM.from_sql_row(rows[0], files_rows) )
    
if __name__ == '__main__':
  unit_test.main()
