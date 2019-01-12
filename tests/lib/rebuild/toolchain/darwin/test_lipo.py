#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path
from bes.fs import file_util, temp_file
from rebuild.toolchain.darwin import lipo
from bes.system import host
from bes.testing.unit_test.unit_test_skip import raise_skip_if_not_platform
from bes.testing.unit_test import unit_test

class test_lipo(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/binary_objects'

  @classmethod
  def setUpClass(clazz):
    raise_skip_if_not_platform(host.MACOS)
    
  def test_archs_fat(self):
    actual_archs = self._archs('fat_fruits.a')
    expected_archs = [ 'arm64', 'armv7', 'i386', 'x86_64' ]
    self.assertEqual( expected_archs, actual_archs )
    
  def test_archs_thin(self):
    self.assertEqual( [ 'i386' ], self._archs('libi386.a') )
    self.assertEqual( [ 'arm64' ], self._archs('libarm64.a') )
    self.assertEqual( [ 'armv7' ], self._archs('libarmv7.a') )
    self.assertEqual( [ 'x86_64' ], self._archs('libx86_64.a') )

    with self.assertRaises(RuntimeError) as context:
      self._archs('notalib.txt')

  def test_archive_is_fat(self):
    self.assertFalse( self._archive_is_fat('libi386.a') )
    self.assertFalse( self._archive_is_fat('libarm64.a') )
    self.assertFalse( self._archive_is_fat('libarmv7.a') )
    self.assertFalse( self._archive_is_fat('libx86_64.a') )
    self.assertTrue( self._archive_is_fat('fat_fruits.a') )

    with self.assertRaises(RuntimeError) as context:
      self._archive_is_fat('notalib.txt')

  def test_fat_to_thin(self):
    tmp_dir = temp_file.make_temp_dir()
    fat_archive = self._test_file('fat_fruits.a')

    for arch in lipo.POSSIBLE_ARCHS:
      thin_archive = path.join(tmp_dir, '%s_fruits.a' % (arch))
      fat_checksum_before = file_util.checksum('sha256', fat_archive)
      lipo.fat_to_thin(fat_archive, thin_archive, arch)
      self.assertTrue( path.exists(thin_archive) )
      self.assertEqual( fat_checksum_before, file_util.checksum('sha256', fat_archive) )
      self.assertEqual( [ arch ], self._archs(thin_archive) )
    
  def test_thin_to_fat(self):
    tmp_dir = temp_file.make_temp_dir()
    thin_archives = [ self._test_file('lib%s.a' % (arch)) for arch in lipo.POSSIBLE_ARCHS]
    fat_archive = path.join(tmp_dir, 'tmp_fat_fruits.a')
    thin_checksums_before = [ file_util.checksum('sha256', thin_archive) for thin_archive in thin_archives ]
    lipo.thin_to_fat(thin_archives, fat_archive)
    thin_checksums_after = [ file_util.checksum('sha256', thin_archive) for thin_archive in thin_archives ]
    self.assertTrue( path.exists(fat_archive) )
    self.assertEqual( thin_checksums_before, thin_checksums_after )
    self.assertEqual( lipo.POSSIBLE_ARCHS, self._archs(fat_archive) )
    
  def _test_file(self, filename):
    return self.platform_data_path(filename)

  def _archs(self, archive):
    return lipo.archs(self._test_file(archive))

  def _archive_is_fat(self, archive):
    return lipo.archive_is_fat(self._test_file(archive))

  def test_is_valid_object(self):
    self.assertTrue( lipo.is_valid_object(self._test_file('cherry.o')) )
    self.assertTrue( lipo.is_valid_object(self._test_file('fat_fruits.a')) )
    self.assertTrue( lipo.is_valid_object(self._test_file('libarm64.a')) )
    self.assertTrue( lipo.is_valid_object(self._test_file('libi386.a')) )
    self.assertTrue( lipo.is_valid_object(self._test_file('fat_32_fruits.so')) )
    self.assertTrue( lipo.is_valid_object(self._test_file('thin_fruits_arm64.so')) )
    self.assertFalse( lipo.is_valid_object(self._test_file('notalib.txt')) )
    
if __name__ == '__main__':
  unit_test.main()
