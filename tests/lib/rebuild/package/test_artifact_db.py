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

  TEST_FILES2 = package_files(FCL(
    [
      ( 'g1', 'gchk1' ),
      ( 'g2', 'gchk2' ),
    ]),
    FCL([
      ( 'h1', 'hchk1' ),
      ( 'h2', 'hchk2' ),
    ]),
    'files2_chk',
    'env_files2_chk')
  
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
    
  def test_readd(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e = PM('foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', [ 'x86_64' ], '', [], {}, self.TEST_FILES)
    adesc = e.artifact_descriptor
    self.assertFalse( db.has_artifact(adesc) )
    db.add_artifact(e)
    self.assertTrue( db.has_artifact(adesc) )
    db.remove_artifact(adesc)
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

  def test_replace(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e1 = PM('foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', [ 'x86_64' ], '', [], {}, self.TEST_FILES)
    e2 = PM('foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', [ 'x86_64' ], '', [], {}, self.TEST_FILES2)
    self.assertFalse( db.has_artifact(e1.artifact_descriptor) )
    db.add_artifact(e1)
    self.assertTrue( db.has_artifact(e1.artifact_descriptor) )
    db.replace_artifact(e2)
      
  def test_replace_not_installed(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e1 = PM('foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', [ 'x86_64' ], '', [], {}, self.TEST_FILES)
    e2 = PM('foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', [ 'x86_64' ], '', [], {}, self.TEST_FILES2)
    self.assertFalse( db.has_artifact(e1.artifact_descriptor) )
    with self.assertRaises(NotInstalledError) as context:
      db.replace_artifact(e2)

  def test_find(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e = PM('foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', [ 'x86_64' ], '', [], {}, self.TEST_FILES)
    adesc = e.artifact_descriptor
    self.assertEqual( None, db.find_artifact(adesc) )
    db.add_artifact(e)
    self.assertEqual( e, db.find_artifact(adesc) )
    db.remove_artifact(adesc)
    self.assertEqual( None, db.find_artifact(adesc) )
      
  def test_get(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e = PM('foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', [ 'x86_64' ], '', [], {}, self.TEST_FILES)
    adesc = e.artifact_descriptor
    with self.assertRaises(NotInstalledError) as context:
      db.get_artifact(adesc)
    db.add_artifact(e)
    self.assertEqual( e, db.get_artifact(adesc) )
    db.remove_artifact(adesc)
    with self.assertRaises(NotInstalledError) as context:
      db.get_artifact(adesc)
      
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
