#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.test import unit_test_helper
from rebuild import binary_format_macho as macho

class test_binary_format_macho(unit_test_helper):

  __unit_test_data_dir__ = 'test_data/binary_objects'

  def test_is_binary(self):
    self.assertTrue( self.__is_binary('macos/fat_fruits.so') )
    self.assertFalse( self.__is_binary('macos/thin_fruits_arm64.a') )
    self.assertFalse( self.__is_binary('macos/thin_fruits_armv7.a') )
    self.assertFalse( self.__is_binary('macos/thin_fruits_i386.a') )
    self.assertFalse( self.__is_binary('macos/thin_fruits_x86_64.a') )
    self.assertFalse( self.__is_binary('macos/notalib.txt') )
    self.assertTrue( self.__is_binary('macos/thin_program_i386.exe') )
    self.assertTrue( self.__is_binary('macos/thin_program_x86_64.exe') )
    self.assertTrue( self.__is_binary('macos/fat_program.exe') )
    self.assertTrue( self.__is_binary('macos/thin_fruits_arm64.so') )
    self.assertTrue( self.__is_binary('macos/thin_fruits_armv7.so') )
    self.assertTrue( self.__is_binary('macos/thin_fruits_i386.so') )
    self.assertTrue( self.__is_binary('macos/thin_fruits_x86_64.so') )
    self.assertTrue( self.__is_binary('macos/fat_all_kiwi.o') )
    self.assertTrue( self.__is_binary('macos/fat_64_kiwi.o') )
    self.assertTrue( self.__is_binary('macos/fat_32_kiwi.o') )
    self.assertTrue( self.__is_binary('macos/thin_kiwi.o') )
    self.assertTrue( self.__is_binary('macos/fat_avocado.o') )
    self.assertTrue( self.__is_binary('macos/thin_cherry.o') )
    self.assertFalse( self.__is_binary('macos/libarm64.a') )
    self.assertTrue( self.__is_binary('macos/libarm64.so') )
    self.assertFalse( self.__is_binary('macos/libarmv7.a') )
    self.assertTrue( self.__is_binary('macos/libarmv7.so') )
    self.assertFalse( self.__is_binary('macos/libi386.a') )
    self.assertTrue( self.__is_binary('macos/libi386.so') )
    self.assertFalse( self.__is_binary('macos/libx86_64.a') )
    self.assertTrue( self.__is_binary('macos/libx86_64.so') )

  def test_read_magic_thin_dot_o(self):
    self.assertEqual( macho.MAGIC_CFFAEDFE, self.__read_magic('macos/thin_arm64_avocado.o') )
    self.assertEqual( macho.MAGIC_CEFAEDFE, self.__read_magic('macos/thin_armv7_avocado.o') )
    self.assertEqual( macho.MAGIC_CEFAEDFE, self.__read_magic('macos/thin_i386_avocado.o') )
    self.assertEqual( macho.MAGIC_CFFAEDFE, self.__read_magic('macos/thin_x86_64_avocado.o') )

  def test_read_magic_fat_dot_o(self):
    self.assertEqual( macho.MAGIC_CAFEBABE, self.__read_magic('macos/fat_avocado.o') )
    self.assertEqual( macho.MAGIC_CAFEBABE, self.__read_magic('macos/fat_all_cherry.o') )
    self.assertEqual( macho.MAGIC_CAFEBABE, self.__read_magic('macos/fat_32_cherry.o') )
    self.assertEqual( macho.MAGIC_CAFEBABE, self.__read_magic('macos/fat_64_cherry.o') )

  def test_read_magic_thin_static(self):
    self.assertEqual( None, self.__read_magic('macos/thin_fruits_arm64.a') )
    self.assertEqual( None, self.__read_magic('macos/thin_fruits_armv7.a') )
    self.assertEqual( None, self.__read_magic('macos/thin_fruits_i386.a') )
    self.assertEqual( None, self.__read_magic('macos/thin_fruits_x86_64.a') )

  def test_read_magic_fat_static(self):
    self.assertEqual( macho.MAGIC_CAFEBABE, self.__read_magic('macos/fat_32_fruits.a') )
    self.assertEqual( macho.MAGIC_CAFEBABE, self.__read_magic('macos/fat_64_fruits.a') )
    self.assertEqual( macho.MAGIC_CAFEBABE, self.__read_magic('macos/fat_all_fruits.a') )

  def test_read_magic_thin_exe(self):
    self.assertEqual( macho.MAGIC_CFFAEDFE, self.__read_magic('macos/thin_program_x86_64.exe') )
    self.assertEqual( macho.MAGIC_CEFAEDFE, self.__read_magic('macos/thin_program_i386.exe') )

  def test_read_magic_fat_exe(self):
    self.assertEqual( macho.MAGIC_CAFEBABE, self.__read_magic('macos/fat_program.exe') )

  def test_read_magic_thin_shared(self):
    self.assertEqual( macho.MAGIC_CFFAEDFE, self.__read_magic('macos/thin_fruits_arm64.so') )
    self.assertEqual( macho.MAGIC_CEFAEDFE, self.__read_magic('macos/thin_fruits_armv7.so') )
    self.assertEqual( macho.MAGIC_CEFAEDFE, self.__read_magic('macos/thin_fruits_i386.so') )
    self.assertEqual( macho.MAGIC_CFFAEDFE, self.__read_magic('macos/thin_fruits_x86_64.so') )

  def test_read_magic_fat_shared(self):
    self.assertEqual( macho.MAGIC_CAFEBABE, self.__read_magic('macos/fat_all_fruits.so') )
    self.assertEqual( macho.MAGIC_CAFEBABE, self.__read_magic('macos/fat_32_fruits.so') )
    self.assertEqual( macho.MAGIC_CAFEBABE, self.__read_magic('macos/fat_64_fruits.so') )
    
  def test_read_magic_fat_empty_file(self):
    self.assertEqual( None, self.__read_magic('macos/empty.txt') )

  def test_read_magic_fat_small_files(self):
    self.assertEqual( None, self.__read_magic('macos/size1.txt') )
    self.assertEqual( None, self.__read_magic('macos/size2.txt') )
    self.assertEqual( None, self.__read_magic('macos/size3.txt') )
    self.assertEqual( None, self.__read_magic('macos/size4.txt') )
    self.assertEqual( None, self.__read_magic('macos/size5.txt') )
    self.assertEqual( None, self.__read_magic('macos/size6.txt') )
    self.assertEqual( None, self.__read_magic('macos/size7.txt') )

  def test_read_magic_junk_files(self):
    self.assertEqual( None, self.__read_magic('macos/notalib.txt') )

  def __is_binary(self, filename):
    return macho().is_binary(self.data_path(filename))
  
  def __read_magic(self, filename):
    return macho().read_magic(self.data_path(filename))
  
if __name__ == '__main__':
  unit_test_helper.main()
