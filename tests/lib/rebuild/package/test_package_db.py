#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import temp_file
from rebuild.base import build_system, package_descriptor as PD, requirement_list as RL
from rebuild.package.package_db import package_db as DB
from rebuild.package.package_db_entry import package_db_entry as PE
from rebuild.package import package_manifest
from bes.debug import debug_timer
from rebuild.package.package_file_list import package_file_list as FCL

class test_package_db(unit_test):

  DEBUG = unit_test.DEBUG
  
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

  def test_db_add(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    self.assertFalse( db.has_package('foo') )
    files = package_manifest(FCL([ ( 'f1', 'c1', 0 ), ( 'f2', 'c2', 0 ) ]), FCL([ ( 'e1', 'ec1', 0 ), ( 'e2', 'ec2', 0 ) ]), 'f_chk')
    reqs = None
    new_entry = PE('foo', '1.2.3', 1, 0, RL(), {}, files)
    db.add_package(new_entry)
    self.assertTrue( db.has_package('foo') )
    self.assertEqual( [ 'foo' ], db.list_all() )
    self.assertEqual( [ 'foo-1.2.3-1' ], db.list_all(include_version = True) )
    self.assertEqual( [ PD.parse('foo-1.2.3-1') ], db.descriptors() )
    self.assertEqual( PE('foo', '1.2.3', 1, 0, RL(), {}, files), db.find_package('foo') )
  
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
    files = package_manifest(FCL([ ( 'f1', 'c1', 0 ), ( 'f2', 'c2', 0 ) ]), FCL([ ( 'e1', 'ec1', 0 ), ( 'e2', 'ec2', 0 ) ]), 'f_chk')
    reqs = None
    new_entry = PE('foo', '1.2.3', 1, 0, RL(), {}, files)
    db.add_package(new_entry)
    self.assertTrue( db.has_package('foo') )
    self.assertEqual( [ 'foo' ], db.list_all() )
    self.assertEqual( PE('foo', '1.2.3', 1, 0, RL(), {}, files), db.find_package('foo') )

    db.remove_package('foo')
    self.assertFalse( db.has_package('foo') )
    self.assertEqual( [], db.list_all() )
    self.assertEqual( None, db.find_package('foo') )

    del db
    recreated_db = DB(tmp_db)
    self.assertFalse( recreated_db.has_package('foo') )
    self.assertEqual( [], recreated_db.list_all() )
    self.assertEqual( None, recreated_db.find_package('foo') )

  def test_package_manifest(self):
    db = DB(self._make_tmp_db_path())
    db.add_package(PE('p1', '1', 0, 0, RL(), {}, package_manifest(FCL([ ( 'p1/f1', 'c1a', 0 ), ( 'p1/f2', 'c1b', 0 ) ]), FCL([ ( 'p1/e1a', 'ec1a', 0 ), ( 'p1/e2b', 'ec1b', 0 ) ]), 'f_chk')))
    db.add_package(PE('p2', '1', 0, 0, RL(), {}, package_manifest(FCL([ ( 'p2/f1', 'c2a', 0 ), ( 'p2/f2', 'c2b', 0 ) ]), FCL([ ( 'p2/e2a', 'ec2a', 0 ), ( 'p2/e2b', 'ec2b', 0 ) ]), 'f_chk')))
    db.add_package(PE('p3', '1', 0, 0, RL(), {}, package_manifest(FCL([ ( 'p3/f1', 'c3a', 0 ), ( 'p3/f2', 'c3b', 0 ) ]), FCL([ ( 'p3/e3a', 'ec3a', 0 ), ( 'p3/e2b', 'ec3b', 0 ) ]), 'f_chk')))
    db.add_package(PE('p4', '1', 0, 0, RL(), {}, package_manifest(FCL([ ( 'p4/f1', 'c4a', 0 ), ( 'p4/f2', 'c4b', 0 ) ]), FCL([ ( 'p4/e4a', 'ec4a', 0 ), ( 'p4/e2b', 'ec4b', 0 ) ]), 'f_chk')))
    db.add_package(PE('p5', '1', 0, 0, RL(), {}, package_manifest(FCL([ ( 'p5/f1', 'c5a', 0 ), ( 'p5/f2', 'c5b', 0 ) ]), FCL([ ( 'p5/e5a', 'ec5a', 0 ), ( 'p5/e2b', 'ec5b', 0 ) ]), 'f_chk')))
     db.add_package(PE('p6', '1', 0, 0, RL(), {}, package_manifest(FCL([ ( 'p6/f1', 'c6a', 0 ), ( 'p6/f2', 'c6b', 0 ) ]), FCL([ ( 'p6/e6a', 'ec6a', 0 ), ( 'p6/e2b', 'ec6b', 0 ) ]), 'f_chk')))
    self.assertEqual( set([ 'p1/f1', 'p1/f2' ]), db.files('p1') )
    self.assertEqual( set([ 'p1/e1a', 'p1/e2b' ]), db.env_files('p1') )

    self.assertEqual( set([ 'p2/f1', 'p2/f2' ]), db.files('p2') )
    self.assertEqual( set([ 'p2/e2a', 'p2/e2b' ]), db.env_files('p2') )

    self.assertEqual( set([ 'p3/f1', 'p3/f2' ]), db.files('p3') )
    self.assertEqual( set([ 'p3/e3a', 'p3/e2b' ]), db.env_files('p3') )

    self.assertEqual( set([ 'p4/f1', 'p4/f2' ]), db.files('p4') )
    self.assertEqual( set([ 'p4/e4a', 'p4/e2b' ]), db.env_files('p4') )

    self.assertEqual( set([ 'p5/f1', 'p5/f2' ]), db.files('p5') )
    self.assertEqual( set([ 'p5/e5a', 'p5/e2b' ]), db.env_files('p5') )

    self.assertEqual( set([ 'p6/f1', 'p6/f2' ]), db.files('p6') )
    self.assertEqual( set([ 'p6/e6a', 'p6/e2b' ]), db.env_files('p6') )
  
  def test_packages_with_files(self):
    db = DB(self._make_tmp_db_path())
    db.add_package(PE('p1', '1', 0, 0, RL(), {}, package_manifest(FCL([ ( 'p1/f1', 'c1', 0 ), ( 'p1/f2', 'c2', 0 ) ]), FCL([ ( 'e1', 'ec1', 0 ), ( 'e2', 'ec2', 0 ) ]), 'f_chk')))
    db.add_package(PE('p2', '1', 0, 0, RL(), {}, package_manifest(FCL([ ( 'p2/f1', 'c1', 0 ), ( 'p2/f2', 'c2', 0 ) ]), FCL([ ( 'e1', 'ec1', 0 ), ( 'e2', 'ec2', 0 ) ]), 'f_chk')))
    db.add_package(PE('p3', '1', 0, 0, RL(), {}, package_manifest(FCL([ ( 'p3/f1', 'c1', 0 ), ( 'p3/f2', 'c2', 0 ) ]), FCL([ ( 'e1', 'ec1', 0 ), ( 'e2', 'ec2', 0 ) ]), 'f_chk')))
    db.add_package(PE('p4', '1', 0, 0, RL(), {}, package_manifest(FCL([ ( 'p4/f1', 'c1', 0 ), ( 'p4/f2', 'c2', 0 ) ]), FCL([ ( 'e1', 'ec1', 0 ), ( 'e2', 'ec2', 0 ) ]), 'f_chk')))
    db.add_package(PE('p5', '1', 0, 0, RL(), {}, package_manifest(FCL([ ( 'p5/f1', 'c1', 0 ), ( 'p5/f2', 'c2', 0 ) ]), FCL([ ( 'e1', 'ec1', 0 ), ( 'e2', 'ec2', 0 ) ]), 'f_chk')))
    db.add_package(PE('p6', '1', 0, 0, RL(), {}, package_manifest(FCL([ ( 'p6/f1', 'c1', 0 ), ( 'p6/f2', 'c2', 0 ) ]), FCL([ ( 'e1', 'ec1', 0 ), ( 'e2', 'ec2', 0 ) ]), 'f_chk')))

    self.assertEqual( [], db.packages_with_files([ 'notthere' ]) )
    self.assertEqual( [ 'p1' ], db.packages_with_files([ 'p1/f2' ]) )
    self.assertEqual( [ 'p1', 'p2' ], db.packages_with_files([ 'p1/f2', 'p2/f1' ]) )
    self.assertEqual( [ 'p1', 'p2', 'p6' ], db.packages_with_files([ 'p1/f2', 'p2/f1', 'p6/f1' ]) )

  def xtest_performance(self):
    db = DB(self._make_tmp_db_path())
    TEST_REQUIREMENTS = RL.parse('foo >= 1.2.3-1 bar >= 6.6.6-1', default_system_mask = build_system.ALL)
    TEST_FILES = FCL([ ( 'lib/libfoo.a', 'c1' ), ( 'include/libfoo.h', 'c2' ) ])
    TEST_PROPERTIES = { 'p1': 'v1', 'p2': 6 }

    t = debug_timer('x', level = 'error')
    n = 1000
    t.start('insert %d ()' % (n))
    for i in range(1, n + 1):
      name = 'n%s' % (i)
      version = '1.0.0'
      files = FCL([ ( 'lib/libfoo%s.a' % (i), 'c1' ), ( 'include/libfoo%s.h' % (i), 'c2' ) ])
      p = PE(name, version, 0, 0, TEST_REQUIREMENTS, TEST_PROPERTIES, files)
      db.add_package(p)
    t.stop()

    t.start('%s: list_all()')
    db.list_all()
    t.stop()

    t.start('%s: names()')
    names = db.names()
    print(len(names))
    for name in names:
      files = db.files(name)
      #print('%s: %s' % (name, len(files)))
    t.stop()

if __name__ == '__main__':
  unit_test.main()
