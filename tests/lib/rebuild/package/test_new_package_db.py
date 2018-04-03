#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest
from bes.fs import temp_file
from rebuild.base import package_descriptor
from rebuild.package.new_package_db import new_package_db as DB
from rebuild.package.new_package_db_entry import new_package_db_entry as PE

class test_package_db(unittest.TestCase):

  def _make_tmp_db_path(self):
    tmp_dir = temp_file.make_temp_dir()
    return path.join(tmp_dir, 'db.sqlite')

  def test_db_create_empty(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    self.assertEqual( [], db.list_all() )

  def test_db_recreate_empty(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    self.assertEqual( [], db.list_all() )
    del db
    recreated_db = DB(tmp_db)
    self.assertEqual( [], recreated_db.list_all() )

  def test_db_add(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    self.assertFalse( db.has_package('foo') )
    files = [ 'lib/libfoo.a', 'include/libfoo.h' ]
    reqs = None
    new_entry = PE('foo', '1.2.3', 1, 0, [], {}, files)
    db.add_package(new_entry)
    self.assertTrue( db.has_package('foo') )
    self.assertEqual( [ 'foo' ], db.list_all() )
    self.assertEqual( PE('foo', '1.2.3', 1, 0, [], {}, files), db.find_package('foo') )
  
    del db
    recreated_db = DB(tmp_db)
    self.assertTrue( recreated_db.has_package('foo') )
    self.assertEqual( [ 'foo' ], recreated_db.list_all() )
    actual_package = recreated_db.find_package('foo')
    expected_package = PE('foo', '1.2.3', 1, 0, [], {}, files)
    self.assertEqual( expected_package, actual_package )

  def test_db_remove(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    self.assertFalse( db.has_package('foo') )
    files = [ 'lib/libfoo.a', 'include/libfoo.h' ]
    reqs = None
    new_entry = PE('foo', '1.2.3', 1, 0, [], {}, files)
    db.add_package(new_entry)
    self.assertTrue( db.has_package('foo') )
    self.assertEqual( [ 'foo' ], db.list_all() )
    self.assertEqual( PE('foo', '1.2.3', 1, 0, [], {}, files), db.find_package('foo') )

    db.remove_package('foo')
    self.assertFalse( db.has_package('foo') )
    self.assertEqual( [], db.list_all() )
    self.assertEqual( None, db.find_package('foo') )

    del db
    recreated_db = DB(tmp_db)
    self.assertFalse( recreated_db.has_package('foo') )
    self.assertEqual( [], recreated_db.list_all() )
    self.assertEqual( None, recreated_db.find_package('foo') )

  def test_packages_with_files(self):
    pass
  
if __name__ == '__main__':
  unittest.main()
