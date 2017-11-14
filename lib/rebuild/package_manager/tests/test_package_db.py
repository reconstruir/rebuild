#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest
from bes.fs import temp_file
from rebuild.base import package_descriptor
from rebuild.package_manager.package_db import package_db
from rebuild.package_manager.package_db_entry import package_db_entry

class test_package_db(unittest.TestCase):

  def __make_tmp_db_path(self):
    tmp_dir = temp_file.make_temp_dir()
    return path.join(tmp_dir, 'db')

  def test_db_create_empty(self):
    tmp_db = self.__make_tmp_db_path()
    db = package_db(tmp_db)
    self.assertFalse( path.isfile(tmp_db) )
    self.assertEqual( [], db.list_all() )

  def test_db_recreate_empty(self):
    tmp_db = self.__make_tmp_db_path()
    db = package_db(tmp_db)
    self.assertFalse( path.isfile(tmp_db) )
    self.assertEqual( [], db.list_all() )
    del db

    recreated_db = package_db(tmp_db)
    self.assertEqual( [], recreated_db.list_all() )

  def test_db_add(self):
    tmp_db = self.__make_tmp_db_path()
    db = package_db(tmp_db)
    self.assertFalse( db.has_package('foo') )
    files = [ 'lib/libfoo.a', 'include/libfoo.h' ]
    reqs = None
    info = package_descriptor('foo', '1.2.3-1', reqs)
    db.add_package(info, files)
    self.assertTrue( db.has_package('foo') )
    self.assertEqual( [ 'foo' ], db.list_all() )
    self.assertEqual( package_db_entry(package_descriptor('foo', '1.2.3-1', reqs), files), db.find_package('foo') )

    del db
    recreated_db = package_db(tmp_db)
    self.assertTrue( recreated_db.has_package('foo') )
    self.assertEqual( [ 'foo' ], recreated_db.list_all() )
    actual_package = recreated_db.find_package('foo')
    expected_package = package_db_entry(package_descriptor('foo', '1.2.3-1', reqs), files)
    self.assertEqual( expected_package, actual_package )

  def test_db_remove(self):
    tmp_db = self.__make_tmp_db_path()
    db = package_db(tmp_db)
    self.assertFalse( db.has_package('foo') )
    files = [ 'lib/libfoo.a', 'include/libfoo.h' ]
    reqs = None
    info = package_descriptor('foo', '1.2.3', '1', reqs)
    db.add_package(info, files)
    self.assertTrue( db.has_package('foo') )
    self.assertEqual( [ 'foo' ], db.list_all() )
    self.assertEqual( package_db_entry(package_descriptor('foo', '1.2.3', '1', reqs), files), db.find_package('foo') )

    db.remove_package('foo')
    self.assertFalse( db.has_package('foo') )
    self.assertEqual( [], db.list_all() )
    self.assertEqual( None, db.find_package('foo') )

    del db
    recreated_db = package_db(tmp_db)
    self.assertFalse( recreated_db.has_package('foo') )
    self.assertEqual( [], recreated_db.list_all() )
    self.assertEqual( None, recreated_db.find_package('foo') )

if __name__ == '__main__':
  unittest.main()
