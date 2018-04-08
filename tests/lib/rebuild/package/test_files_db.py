#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_checksum_list, temp_file
from bes.sqlite import sqlite
from rebuild.package.files_db import files_db as DB

class test_files_db(unit_test):

  TEST_FILES = [
    ( 'f1', 'chk1' ),
    ( 'f2', 'chk2' ),
  ]

  TEST_FILES_CHECKSUMS = file_checksum_list(TEST_FILES)

  DEBUG = unit_test.DEBUG
  
  def test_add(self):
    db = self._make_tmp_db()
    self.assertFalse( db.has_table('foo') )
    db.add_table('foo', self.TEST_FILES_CHECKSUMS)
    self.assertTrue( db.has_table('foo') )
    self.assertEqual( self.TEST_FILES, db.file_checksums_rows('foo') )
    self.assertEqual( [ ( 'f1', ), ( 'f2', ) ], db.filenames_rows('foo') )
    self.assertEqual( self.TEST_FILES_CHECKSUMS, db.file_checksums('foo') )
    self.assertEqual( [ 'f1', 'f2' ], db.filenames('foo') )
                      
  def test_remove(self):
    db = self._make_tmp_db()
    self.assertFalse( db.has_table('foo') )
    db.add_table('foo', self.TEST_FILES_CHECKSUMS)
    self.assertTrue( db.has_table('foo') )
    db.remove_table('foo')
    self.assertFalse( db.has_table('foo') )
                      
  def _make_tmp_db_path(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    f = path.join(tmp_dir, 'db.sqlite')
    if self.DEBUG:
      self.spew('_make_tmp_db_path() => %s' % (f))
    return f

  def _make_tmp_db(self):
    return DB(sqlite(self._make_tmp_db_path()))
  
if __name__ == '__main__':
  unit_test.main()
