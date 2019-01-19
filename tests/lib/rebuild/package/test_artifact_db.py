#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import temp_file
from rebuild.base import artifact_descriptor as AD, build_level, build_system, build_target as BT, package_descriptor as PD, requirement_list as RL
from rebuild.package.artifact_db import artifact_db as DB
from rebuild.package.db_error import *
from rebuild.package.package_metadata import package_metadata as PM
from bes.debug import debug_timer
from rebuild.package import package_manifest
from rebuild.package.package_file_list import package_file_list as FCL

class test_artifact_db(unit_test):

  TEST_MANIFEST = package_manifest(FCL(
    [
      ( 'f1', 'fchk1', 0 ),
      ( 'f2', 'fchk2', 0 ),
    ]),
    FCL([
      ( 'e1', 'echk1', 0 ),
      ( 'e2', 'echk2', 0 ),
    ]),
    'manifest_chk')

  TEST_MANIFEST2 = package_manifest(FCL(
    [
      ( 'g1', 'gchk1', 0 ),
      ( 'g2', 'gchk2', 0 ),
    ]),
    FCL([
      ( 'h1', 'hchk1', 0 ),
      ( 'h2', 'hchk2', 0 ),
    ]),
    'manifest2_chk')
  
  DEBUG = unit_test.DEBUG
  #DEBUG = True

  LINUX_BT = BT('linux', 'ubuntu', '18', '', ( 'x86_64', ), 'release')
  MACOS_BT = BT('macos', '', '10', '13', ( 'x86_64', ), 'release')
  
  def _make_tmp_db_path(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    f = path.join(tmp_dir, 'db.sqlite')
    if self.DEBUG:
      self.spew('_make_tmp_db_path() => %s' % (f))
    return f

  def test_db_create_empty(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    self.assertEqual( [], db.list_all_by_descriptor() )

  def test_db_recreate_empty(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    self.assertEqual( [], db.list_all_by_descriptor() )
    del db
    recreated_db = DB(tmp_db)
    self.assertEqual( [], recreated_db.list_all_by_descriptor() )

  def test_add(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST)
    adesc = e.artifact_descriptor
    self.assertFalse( db.has_artifact(adesc) )
    db.add_artifact(e)
    self.assertTrue( db.has_artifact(adesc) )

  def test_add_two(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)

    e1 = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST)
    adesc1 = e1.artifact_descriptor
    self.assertFalse( db.has_artifact(adesc1) )
    db.add_artifact(e1)
    self.assertTrue( db.has_artifact(adesc1) )
    
    e2 = PM(2, 'foo-1.2.4.tar.gz', 'foo', '1.2.4', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST)
    adesc2 = e2.artifact_descriptor
    self.assertFalse( db.has_artifact(adesc2) )
    db.add_artifact(e2)
    self.assertTrue( db.has_artifact(adesc2) )

  def test_add_persistent(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e1 = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST)
    adesc1 = e1.artifact_descriptor
    self.assertFalse( db.has_artifact(adesc1) )
    db.add_artifact(e1)
    self.assertTrue( db.has_artifact(adesc1) )
    e2 = PM(2, 'foo-1.2.4.tar.gz', 'foo', '1.2.4', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST)
    adesc2 = e2.artifact_descriptor
    self.assertFalse( db.has_artifact(adesc2) )
    db.add_artifact(e2)
    self.assertTrue( db.has_artifact(adesc2) )
    db = DB(tmp_db)
    self.assertTrue( db.has_artifact(adesc1) )
    self.assertTrue( db.has_artifact(adesc2) )
    
  def test_add_duplicate(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST)
    adesc = e.artifact_descriptor
    self.assertFalse( db.has_artifact(adesc) )
    db.add_artifact(e)
    self.assertTrue( db.has_artifact(adesc) )
    with self.assertRaises(AlreadyInstalledError) as context:
      db.add_artifact(e)
      
  def test_remove(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST)
    adesc = e.artifact_descriptor
    self.assertFalse( db.has_artifact(adesc) )
    db.add_artifact(e)
    self.assertTrue( db.has_artifact(adesc) )
    db.remove_artifact(adesc)
    self.assertFalse( db.has_artifact(adesc) )
    
  def test_readd(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST)
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
    e = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST)
    adesc = e.artifact_descriptor
    self.assertFalse( db.has_artifact(adesc) )
    with self.assertRaises(NotInstalledError) as context:
      db.remove_artifact(adesc)

  def test_replace(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e1 = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '10', '', '', [], {}, self.TEST_MANIFEST)
    e2 = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '10', '', '', [], {}, self.TEST_MANIFEST2)
  #  self.assertFalse( db.has_artifact(e1.artifact_descriptor) )

    db.add_artifact(e1)
    return
  
    self.assertTrue( db.has_artifact(e1.artifact_descriptor) )
    md1 = db.list_all_by_metadata()
    self.assertEqual( md1, db.list_all_by_metadata() )
    self.assertEqual( self.TEST_MANIFEST, md1[0].manifest )

    db.replace_artifact(e2)
    md2 = db.list_all_by_metadata()
    self.assertEqual( md2, db.list_all_by_metadata() )
      
  def test_replace_not_installed(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e1 = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST)
    e2 = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST2)
    self.assertFalse( db.has_artifact(e1.artifact_descriptor) )
    with self.assertRaises(NotInstalledError) as context:
      db.replace_artifact(e2)

  def test_find(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST)
    adesc = e.artifact_descriptor
    self.assertEqual( None, db.find_artifact(adesc) )
    db.add_artifact(e)
    r = db.find_artifact(adesc)
    print('R: %s' % (str(r)))
    self.assertEqual( e, r )
    db.remove_artifact(adesc)
    self.assertEqual( None, db.find_artifact(adesc) )
    
  def test_get(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST)
    adesc = e.artifact_descriptor
    with self.assertRaises(NotInstalledError) as context:
      db.get_artifact(adesc)
      db.add_artifact(e)
      self.assertEqual( e, db.get_artifact(adesc) )
      db.remove_artifact(adesc)
    with self.assertRaises(NotInstalledError) as context:
      db.get_artifact(adesc)

  def test_list_all_by_descriptor(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e1 = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST)
    e2 = PM(2, 'bar-5.6.7.tar.gz', 'bar', '5.6.7', 1, 0, 'linux', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST2)
    db.add_artifact(e1)
    self.assertEqual( [ e1.artifact_descriptor ], db.list_all_by_descriptor() )
    db.add_artifact(e2)
    self.assertEqual( [ e2.artifact_descriptor, e1.artifact_descriptor ], db.list_all_by_descriptor() )

  def test_list_all_by_descriptor_with_build_target(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e1 = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '10', '13', [], {}, self.TEST_MANIFEST)
    e2 = PM(2, 'bar-5.6.7.tar.gz', 'bar', '5.6.7', 1, 0, 'linux', 'release', ( 'x86_64', ), 'ubuntu', '18', '', [], {}, self.TEST_MANIFEST2)
    db.add_artifact(e1)
    db.add_artifact(e2)
    self.assertEqual( [ e2.artifact_descriptor ], db.list_all_by_descriptor(build_target = self.LINUX_BT) )
    self.assertEqual( [ e1.artifact_descriptor ], db.list_all_by_descriptor(build_target = self.MACOS_BT) )

  def test_list_all_by_descriptor_with_build_target_and_distro(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e1 = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'linux', 'release', ( 'x86_64', ), 'ubuntu', '18', '', [], {}, self.TEST_MANIFEST)
    e2 = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'linux', 'release', ( 'x86_64', ), 'centos', '7', '', [], {}, self.TEST_MANIFEST)
    db.add_artifact(e1)
    db.add_artifact(e2)
    self.assertEqual( [ e1.artifact_descriptor ], db.list_all_by_descriptor(build_target = BT.parse_path('linux-ubuntu-18/x86_64/release')) )
    self.assertEqual( [ e2.artifact_descriptor ], db.list_all_by_descriptor(build_target = BT.parse_path('linux-centos-7/x86_64/release')) )
    
  def test_list_all_by_metadata(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e1 = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '10', '13', [], {}, self.TEST_MANIFEST)
    e2 = PM(2, 'bar-5.6.7.tar.gz', 'bar', '5.6.7', 1, 0, 'linux', 'release', ( 'x86_64', ), 'ubuntu', '18', '', [], {}, self.TEST_MANIFEST2)
    db.add_artifact(e1)
    self.assertEqual( [ e1 ], db.list_all_by_metadata() )
    db.add_artifact(e2)
    self.assertEqual( [ e2, e1 ], db.list_all_by_metadata() )

  def test_list_all_by_metadata_with_build_target(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e1 = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '10', '13', [], {}, self.TEST_MANIFEST)
    e2 = PM(2, 'bar-5.6.7.tar.gz', 'bar', '5.6.7', 1, 0, 'linux', 'release', ( 'x86_64', ), 'ubuntu', '18', '', [], {}, self.TEST_MANIFEST2)
    db.add_artifact(e1)
    db.add_artifact(e2)
    self.assertEqual( [ e2 ], db.list_all_by_metadata(build_target = self.LINUX_BT) )
    self.assertEqual( [ e1 ], db.list_all_by_metadata(build_target = self.MACOS_BT) )
    
  def test_list_all_by_package_descriptor(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e1 = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST)
    e2 = PM(2, 'bar-5.6.7.tar.gz', 'bar', '5.6.7', 1, 0, 'linux', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST2)
    pd1 = PD('foo', '1.2.3-1')
    pd2 = PD('bar', '5.6.7-1')
    db.add_artifact(e1)
    self.assertEqual( [ pd1 ], db.list_all_by_package_descriptor() )
    db.add_artifact(e2)
    self.assertEqual( [ pd1, pd2 ], db.list_all_by_package_descriptor() )

  def test_list_all_by_package_descriptor_with_build_target(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e1 = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '10', '13', [], {}, self.TEST_MANIFEST)
    e2 = PM(2, 'bar-5.6.7.tar.gz', 'bar', '5.6.7', 1, 0, 'linux', 'release', ( 'x86_64', ), 'ubuntu', '18', '', [], {}, self.TEST_MANIFEST2)
    pd1 = PD('foo', '1.2.3-1')
    pd2 = PD('bar', '5.6.7-1')
    db.add_artifact(e1)
    db.add_artifact(e2)
    self.assertEqual( [ pd2 ], db.list_all_by_package_descriptor(build_target = self.LINUX_BT) )
    self.assertEqual( [ pd1 ], db.list_all_by_package_descriptor(build_target = self.MACOS_BT) )

  def test_list_all_version_upgrade(self):
    tmp_db = self._make_tmp_db_path()
    db = DB(tmp_db)
    e1 = PM(2, 'foo-1.2.3.tar.gz', 'foo', '1.2.3', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST)
    e2 = PM(2, 'foo-1.2.4.tar.gz', 'foo', '1.2.4', 1, 0, 'macos', 'release', ( 'x86_64', ), '', '', '', [], {}, self.TEST_MANIFEST)
    pd1 = PD('foo', '1.2.3-1')
    pd2 = PD('foo', '1.2.4-1')
    db.add_artifact(e1)
    self.assertEqual( [ pd1 ], db.list_all_by_package_descriptor() )
    db.add_artifact(e2)
    self.assertEqual( [ pd1, pd2 ], db.list_all_by_package_descriptor() )
    
if __name__ == '__main__':
  unit_test.main()
