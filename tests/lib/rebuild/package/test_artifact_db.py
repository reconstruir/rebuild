#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_checksum_list as FCL, temp_file
from rebuild.base import build_system, package_descriptor as PD, requirement_list as RL
from rebuild.package.artifact_db import artifact_db as DB
from rebuild.package.db_error import *
from rebuild.package import artifact_descriptor as AD
from rebuild.package.package_metadata import package_metadata as PM
from bes.debug import debug_timer
from rebuild.package import package_files

class test_artifact_db(unit_test):

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

  DEBUG = unit_test.DEBUG
  #DEBUG = True
  
  def _make_tmp_db_path(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    f = path.join(tmp_dir, 'db.sqlite')
    if self.DEBUG:
      self.spew('_make_tmp_db_path() => %s' % (f))
    return f

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

  def test_add(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e = PM('foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', [ 'x86_64' ], '', [], {}, self.TEST_FILES)
    adesc = e.artifact_descriptor
    self.assertFalse( db.has_artifact(adesc) )
    db.add_artifact(e)
    self.assertTrue( db.has_artifact(adesc) )

  def test_add_duplicate(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e = PM('foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', [ 'x86_64' ], '', [], {}, self.TEST_FILES)
    adesc = e.artifact_descriptor
    self.assertFalse( db.has_artifact(adesc) )
    db.add_artifact(e)
    self.assertTrue( db.has_artifact(adesc) )
    with self.assertRaises(AlreadyInstalledError) as context:
      db.add_artifact(e)
      
  def test_remove(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e = PM('foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', [ 'x86_64' ], '', [], {}, self.TEST_FILES)
    adesc = e.artifact_descriptor
    self.assertFalse( db.has_artifact(adesc) )
    db.add_artifact(e)
    self.assertTrue( db.has_artifact(adesc) )
    db.remove_artifact(adesc)
    self.assertFalse( db.has_artifact(adesc) )
    
  def test_remove_not_installed(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e = PM('foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', [ 'x86_64' ], '', [], {}, self.TEST_FILES)
    adesc = e.artifact_descriptor
    self.assertFalse( db.has_artifact(adesc) )
    with self.assertRaises(NotInstalledError) as context:
      db.remove_artifact(adesc)
    
  def xtest_db_remove(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    self.assertFalse( db.has_package('foo') )
    files = FCL([ ( 'lib/libfoo.a', 'c1' ), ( 'include/libfoo.h', 'c2' ) ])
    files.sort()
    reqs = None
    new_entry = PM('foo-1.2.3.tar.gz', '1.2.3', 1, 0, 'macos', 'release', [ 'x86_64' ], None, [], {}, [])
    db.add_package(new_entry)
    self.assertTrue( db.has_package('1.2.3', 1, 0, 'macos', 'release', [ 'x86_64' ], None) )
    return
#    self.assertEqual( [ 'foo' ], db.list_all() )
#    self.assertEqual( PM('foo', '1.2.3', 1, 0, [], {}, files), db.find_package('foo') )

    db.remove_package('foo')
    self.assertFalse( db.has_package('foo') )
    self.assertEqual( [], db.list_all() )
    self.assertEqual( None, db.find_package('foo') )

    del db
    recreated_db = DB(tmp_db)
    self.assertFalse( recreated_db.has_package('foo') )
    self.assertEqual( [], recreated_db.list_all() )
    self.assertEqual( None, recreated_db.find_package('foo') )

  def xtest_package_files(self):
    db = DB(self._make_tmp_db_path())
    db.add_package(PM('p1', '1', 0, 0, [], {}, FCL([ ( 'p1/f1', 'c' ), ( 'p1/f2', 'c' ) ])))
    db.add_package(PM('p2', '1', 0, 0, [], {}, FCL([ ( 'p2/f1', 'c' ), ( 'p2/f2', 'c' ) ])))
    db.add_package(PM('p3', '1', 0, 0, [], {}, FCL([ ( 'p3/f1', 'c' ), ( 'p3/f2', 'c' ) ])))
    db.add_package(PM('p4', '1', 0, 0, [], {}, FCL([ ( 'p4/f1', 'c' ), ( 'p4/f2', 'c' ) ])))
    db.add_package(PM('p5', '1', 0, 0, [], {}, FCL([ ( 'p5/f1', 'c' ), ( 'p5/f2', 'c' ) ])))
    db.add_package(PM('p6', '1', 0, 0, [], {}, FCL([ ( 'p6/f1', 'c' ), ( 'p6/f2', 'c' ) ])))
    self.assertEqual( set([ 'p1/f1', 'p1/f2' ]), db.package_files('p1') )
    self.assertEqual( set([ 'p2/f1', 'p2/f2' ]), db.package_files('p2') )
    self.assertEqual( set([ 'p3/f1', 'p3/f2' ]), db.package_files('p3') )
    self.assertEqual( set([ 'p4/f1', 'p4/f2' ]), db.package_files('p4') )
    self.assertEqual( set([ 'p5/f1', 'p5/f2' ]), db.package_files('p5') )
    self.assertEqual( set([ 'p6/f1', 'p6/f2' ]), db.package_files('p6') )
  
  def xtest_packages_with_files(self):
    db = DB(self._make_tmp_db_path())
    db.add_package(PM('p1', '1', 0, 0, [], {}, FCL([ ( 'p1/f1', 'c' ), ( 'p1/f2', 'c' ) ])))
    db.add_package(PM('p2', '1', 0, 0, [], {}, FCL([ ( 'p2/f1', 'c' ), ( 'p2/f2', 'c' ) ])))
    db.add_package(PM('p3', '1', 0, 0, [], {}, FCL([ ( 'p3/f1', 'c' ), ( 'p3/f2', 'c' ) ])))
    db.add_package(PM('p4', '1', 0, 0, [], {}, FCL([ ( 'p4/f1', 'c' ), ( 'p4/f2', 'c' ) ])))
    db.add_package(PM('p5', '1', 0, 0, [], {}, FCL([ ( 'p5/f1', 'c' ), ( 'p5/f2', 'c' ) ])))
    db.add_package(PM('p6', '1', 0, 0, [], {}, FCL([ ( 'p6/f1', 'c' ), ( 'p6/f2', 'c' ) ])))

    self.assertEqual( [], db.packages_with_files([ 'notthere' ]) )
    self.assertEqual( [ 'p1' ], db.packages_with_files([ 'p1/f2' ]) )
    self.assertEqual( [ 'p1', 'p2' ], db.packages_with_files([ 'p1/f2', 'p2/f1' ]) )
    self.assertEqual( [ 'p1', 'p2', 'p6' ], db.packages_with_files([ 'p1/f2', 'p2/f1', 'p6/f1' ]) )

if __name__ == '__main__':
  unit_test.main()
