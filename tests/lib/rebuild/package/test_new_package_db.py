#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest
from bes.fs import file_checksum_list as FCL, temp_file
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
    files = FCL([ ( 'lib/libfoo.a', 'c1' ), ( 'include/libfoo.h', 'c2' ) ])
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
    files = FCL([ ( 'lib/libfoo.a', 'c1' ), ( 'include/libfoo.h', 'c2' ) ])
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

  def test_package_files(self):
    db = DB(self._make_tmp_db_path())
    db.add_package(PE('p1', '1', 0, 0, [], {}, FCL([ ( 'p1/f1', 'c' ), ( 'p1/f2', 'c' ) ])))
    db.add_package(PE('p2', '1', 0, 0, [], {}, FCL([ ( 'p2/f1', 'c' ), ( 'p2/f2', 'c' ) ])))
    db.add_package(PE('p3', '1', 0, 0, [], {}, FCL([ ( 'p3/f1', 'c' ), ( 'p3/f2', 'c' ) ])))
    db.add_package(PE('p4', '1', 0, 0, [], {}, FCL([ ( 'p4/f1', 'c' ), ( 'p4/f2', 'c' ) ])))
    db.add_package(PE('p5', '1', 0, 0, [], {}, FCL([ ( 'p5/f1', 'c' ), ( 'p5/f2', 'c' ) ])))
    db.add_package(PE('p6', '1', 0, 0, [], {}, FCL([ ( 'p6/f1', 'c' ), ( 'p6/f2', 'c' ) ])))
    self.assertEqual( set([ 'p1/f1', 'p1/f2' ]), db.package_files('p1') )
    self.assertEqual( set([ 'p2/f1', 'p2/f2' ]), db.package_files('p2') )
    self.assertEqual( set([ 'p3/f1', 'p3/f2' ]), db.package_files('p3') )
    self.assertEqual( set([ 'p4/f1', 'p4/f2' ]), db.package_files('p4') )
    self.assertEqual( set([ 'p5/f1', 'p5/f2' ]), db.package_files('p5') )
    self.assertEqual( set([ 'p6/f1', 'p6/f2' ]), db.package_files('p6') )
  
  def test_packages_with_files(self):
    db = DB(self._make_tmp_db_path())
    db.add_package(PE('p1', '1', 0, 0, [], {}, FCL([ ( 'p1/f1', 'c' ), ( 'p1/f2', 'c' ) ])))
    db.add_package(PE('p2', '1', 0, 0, [], {}, FCL([ ( 'p2/f1', 'c' ), ( 'p2/f2', 'c' ) ])))
    db.add_package(PE('p3', '1', 0, 0, [], {}, FCL([ ( 'p3/f1', 'c' ), ( 'p3/f2', 'c' ) ])))
    db.add_package(PE('p4', '1', 0, 0, [], {}, FCL([ ( 'p4/f1', 'c' ), ( 'p4/f2', 'c' ) ])))
    db.add_package(PE('p5', '1', 0, 0, [], {}, FCL([ ( 'p5/f1', 'c' ), ( 'p5/f2', 'c' ) ])))
    db.add_package(PE('p6', '1', 0, 0, [], {}, FCL([ ( 'p6/f1', 'c' ), ( 'p6/f2', 'c' ) ])))

    self.assertEqual( [], db.packages_with_files([ 'notthere' ]) )
    self.assertEqual( [ 'p1' ], db.packages_with_files([ 'p1/f2' ]) )
    self.assertEqual( [ 'p1', 'p2' ], db.packages_with_files([ 'p1/f2', 'p2/f1' ]) )
    self.assertEqual( [ 'p1', 'p2', 'p6' ], db.packages_with_files([ 'p1/f2', 'p2/f1', 'p6/f1' ]) )
  
if __name__ == '__main__':
  unittest.main()
