#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path, unittest
from bes.fs import file_checksum, file_util, temp_file
from rebuild.darwin import Lipo
from bes.system import host
from bes.testing.unit_test.unit_test_skip import raise_skip_if_not_platform
from bes.testing.unit_test import unit_test

class test_lipo(unit_test):

  TEST_DATA_DIR = path.abspath(path.join(path.dirname(__file__), 'test_data/binary_objects/macos'))

  @classmethod
  def setUpClass(clazz):
    raise_skip_if_not_platform(host.MACOS)
    
  def test_archs_fat(self):
    actual_archs = self.__archs('fat_fruits.a')
    expected_archs = [ 'arm64', 'armv7', 'i386', 'x86_64' ]
    self.assertEqual( expected_archs, actual_archs )
    
  def test_archs_thin(self):
    self.assertEqual( [ 'i386' ], self.__archs('libi386.a') )
    self.assertEqual( [ 'arm64' ], self.__archs('libarm64.a') )
    self.assertEqual( [ 'armv7' ], self.__archs('libarmv7.a') )
    self.assertEqual( [ 'x86_64' ], self.__archs('libx86_64.a') )

    with self.assertRaises(RuntimeError) as context:
      self.__archs('notalib.txt')

  def test_archive_is_fat(self):
    self.assertFalse( self.__archive_is_fat('libi386.a') )
    self.assertFalse( self.__archive_is_fat('libarm64.a') )
    self.assertFalse( self.__archive_is_fat('libarmv7.a') )
    self.assertFalse( self.__archive_is_fat('libx86_64.a') )
    self.assertTrue( self.__archive_is_fat('fat_fruits.a') )

    with self.assertRaises(RuntimeError) as context:
      self.__archive_is_fat('notalib.txt')

  def test_fat_to_thin(self):
    tmp_dir = temp_file.make_temp_dir()
    fat_archive = self.__test_file('fat_fruits.a')

    for arch in Lipo.POSSIBLE_ARCHS:
      thin_archive = path.join(tmp_dir, '%s_fruits.a' % (arch))
      fat_checksum_before = file_checksum.checksum(fat_archive)
      Lipo.fat_to_thin(fat_archive, thin_archive, arch)
      self.assertTrue( path.exists(thin_archive) )
      self.assertEqual( fat_checksum_before, file_checksum.checksum(fat_archive) )
      self.assertEqual( [ arch ], self.__archs(thin_archive) )
    
  def test_thin_to_fat(self):
    tmp_dir = temp_file.make_temp_dir()
    thin_archives = [ self.__test_file('lib%s.a' % (arch)) for arch in Lipo.POSSIBLE_ARCHS]
    fat_archive = path.join(tmp_dir, 'tmp_fat_fruits.a')
    thin_checksums_before = [ file_checksum.checksum(thin_archive) for thin_archive in thin_archives ]
    Lipo.thin_to_fat(thin_archives, fat_archive)
    thin_checksums_after = [ file_checksum.checksum(thin_archive) for thin_archive in thin_archives ]
    self.assertTrue( path.exists(fat_archive) )
    self.assertEqual( thin_checksums_before, thin_checksums_after )
    self.assertEqual( Lipo.POSSIBLE_ARCHS, self.__archs(fat_archive) )
    
  def __test_file(self, filename):
    return path.join(self.TEST_DATA_DIR, filename)

  def __archs(self, archive):
    return Lipo.archs(self.__test_file(archive))

  def __archive_is_fat(self, archive):
    return Lipo.archive_is_fat(self.__test_file(archive))

  def test_is_valid_object(self):
    self.assertTrue( Lipo.is_valid_object(self.__test_file('cherry.o')) )
    self.assertTrue( Lipo.is_valid_object(self.__test_file('fat_fruits.a')) )
    self.assertTrue( Lipo.is_valid_object(self.__test_file('libarm64.a')) )
    self.assertTrue( Lipo.is_valid_object(self.__test_file('libi386.a')) )
    self.assertTrue( Lipo.is_valid_object(self.__test_file('fat_32_fruits.so')) )
    self.assertTrue( Lipo.is_valid_object(self.__test_file('thin_fruits_arm64.so')) )
    self.assertFalse( Lipo.is_valid_object(self.__test_file('notalib.txt')) )
    
if __name__ == '__main__':
  unittest.main()
