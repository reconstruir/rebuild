#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path
from bes.sqlite import sqlite
from bes.testing.unit_test import unit_test
from bes.fs import file_checksum_list as FCL
from rebuild.base import build_system, build_target, package_descriptor, requirement_list as RL
from rebuild.package.package_metadata import package_metadata as PM
from rebuild.package.artifact_db import artifact_db as DB
from rebuild.package import package_files

class test_package_metadata(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/lib/rebuild/package'

  TEST_REQUIREMENTS = RL.parse('foo >= 1.2.3-1 bar >= 6.6.6-1')
  TEST_FILES = package_files(FCL(
    [
      ( 'f1', 'fchk1' ),
      ( 'f2', 'fchk2' ),
    ]),
    FCL([
      ( 'e1', 'echk1' ),
      ( 'e2', 'echk2' ),
    ]),
    'files_chk',
    'env_files_chk')
    
  TEST_PROPERTIES = { 'p1': 'v1', 'p2': 6 }

  TEST_ENTRY = PM('kiwi-6.7.8-2.tar.gz', 'kiwi', '6.7.8', 2, 0, 'macos', 'release', [ 'x86_64' ], '',
                  TEST_REQUIREMENTS, TEST_PROPERTIES, TEST_FILES)

  def test_descriptor(self):
    self.assertEqual( package_descriptor('kiwi', '6.7.8-2', self.TEST_PROPERTIES, self.TEST_REQUIREMENTS),
                      self.TEST_ENTRY.package_descriptor )

  def test_build_target(self):
    self.assertEqual( build_target('macos', 'release', [ 'x86_64' ], ''), self.TEST_ENTRY.build_target )

  def test_to_json(self):
    self.maxDiff = None
    expected_json = '''\
{
  "_format_version": 2, 
  "archs": [
    "x86_64"
  ], 
  "distro": "", 
  "epoch": 0, 
  "filename": "kiwi-6.7.8-2.tar.gz", 
  "files": {
    "env_files": [
      [
        "e1", 
        "echk1"
      ], 
      [
        "e2", 
        "echk2"
      ]
    ], 
    "env_files_checksum": "env_files_chk", 
    "files": [
      [
        "f1", 
        "fchk1"
      ], 
      [
        "f2", 
        "fchk2"
      ]
    ], 
    "files_checksum": "files_chk"
  }, 
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
  "distro": "", 
  "epoch": 0, 
  "filename": "kiwi-6.7.8-2.tar.gz", 
  "files": {
    "env_files": [
      [
        "e1", 
        "echk1"
      ], 
      [
        "e2", 
        "echk2"
      ]
    ], 
    "env_files_checksum": "env_files_chk", 
    "files": [
      [
        "f1", 
        "fchk1"
      ], 
      [
        "f2", 
        "fchk2"
      ]
    ], 
    "files_checksum": "files_chk"
  }, 
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

  def xtest_to_sql_dict(self):
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
      'distro': '\'\'',
    }
    self.assertEqual( expected, self.TEST_ENTRY.to_sql_dict() )

  def test_clone_with_filename(self):
    self.assertEqual( 'kiwi-6.7.8-2.tar.gz', self.TEST_ENTRY.filename )
    self.assertEqual( 'kiwi', self.TEST_ENTRY.name )
    new_pm = self.TEST_ENTRY.clone_with_filename('foo.tar')
    self.assertEqual( 'foo.tar', new_pm.filename )
    self.assertEqual( 'kiwi', new_pm.name )
    
if __name__ == '__main__':
  unit_test.main()
