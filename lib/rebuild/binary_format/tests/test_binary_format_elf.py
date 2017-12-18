#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.binary_format import binary_format_elf as elf

class test_binary_format_elf(unit_test):

  __unit_test_data_dir__ = '../../test_data/binary_objects'

  def test_name(self):
    self.assertEqual( 'elf', elf().name() )
  
  def test_is_binary(self):
    self.assertTrue( self.__is_binary('linux/cherry.o') )
    self.assertFalse( self.__is_binary('linux/empty.txt') )
    self.assertTrue( self.__is_binary('linux/fat_32_cherry.o') )
    self.assertFalse( self.__is_binary('linux/fat_32_fruits.a') )
    self.assertTrue( self.__is_binary('linux/fat_32_fruits.so') )
    self.assertTrue( self.__is_binary('linux/fat_32_kiwi.o') )
    self.assertTrue( self.__is_binary('linux/fat_64_cherry.o') )
    self.assertFalse( self.__is_binary('linux/fat_64_fruits.a') )
    self.assertTrue( self.__is_binary('linux/fat_64_fruits.so') )
    self.assertTrue( self.__is_binary('linux/fat_64_kiwi.o') )
    self.assertTrue( self.__is_binary('linux/fat_all_cherry.o') )
    self.assertFalse( self.__is_binary('linux/fat_all_fruits.a') )
    self.assertTrue( self.__is_binary('linux/fat_all_fruits.so') )
    self.assertTrue( self.__is_binary('linux/fat_all_kiwi.o') )
    self.assertTrue( self.__is_binary('linux/fat_avocado.o') )
    self.assertTrue( self.__is_binary('linux/fat_cherry.o') )
    self.assertTrue( self.__is_binary('linux/fat_kiwi.o') )
    self.assertTrue( self.__is_binary('linux/fat_main.o') )
    self.assertTrue( self.__is_binary('linux/fat_program.exe') )
    self.assertTrue( self.__is_binary('linux/kiwi.o') )
    self.assertFalse( self.__is_binary('linux/libarm64.a') )
    self.assertTrue( self.__is_binary('linux/libarm64.so') )
    self.assertFalse( self.__is_binary('linux/libarmv7.a') )
    self.assertTrue( self.__is_binary('linux/libarmv7.so') )
    self.assertFalse( self.__is_binary('linux/libi386.a') )
    self.assertTrue( self.__is_binary('linux/libi386.so') )
    self.assertFalse( self.__is_binary('linux/libx86_64.a') )
    self.assertTrue( self.__is_binary('linux/libx86_64.so') )
    self.assertFalse( self.__is_binary('linux/notalib.txt') )
    self.assertFalse( self.__is_binary('linux/size1.txt') )
    self.assertFalse( self.__is_binary('linux/size10.txt') )
    self.assertFalse( self.__is_binary('linux/size2.txt') )
    self.assertFalse( self.__is_binary('linux/size3.txt') )
    self.assertFalse( self.__is_binary('linux/size4.txt') )
    self.assertFalse( self.__is_binary('linux/size5.txt') )
    self.assertFalse( self.__is_binary('linux/size6.txt') )
    self.assertFalse( self.__is_binary('linux/size7.txt') )
    self.assertFalse( self.__is_binary('linux/size8.txt') )
    self.assertFalse( self.__is_binary('linux/size9.txt') )
    self.assertTrue( self.__is_binary('linux/thin_arm64_avocado.o') )
    self.assertTrue( self.__is_binary('linux/thin_armv7_avocado.o') )
    self.assertTrue( self.__is_binary('linux/thin_cherry.o') )
    self.assertFalse( self.__is_binary('linux/thin_fruits_arm64.a') )
    self.assertTrue( self.__is_binary('linux/thin_fruits_arm64.so') )
    self.assertFalse( self.__is_binary('linux/thin_fruits_armv7.a') )
    self.assertTrue( self.__is_binary('linux/thin_fruits_armv7.so') )
    self.assertFalse( self.__is_binary('linux/thin_fruits_i386.a') )
    self.assertTrue( self.__is_binary('linux/thin_fruits_i386.so') )
    self.assertFalse( self.__is_binary('linux/thin_fruits_x86_64.a') )
    self.assertTrue( self.__is_binary('linux/thin_fruits_x86_64.so') )
    self.assertTrue( self.__is_binary('linux/thin_i386_avocado.o') )
    self.assertTrue( self.__is_binary('linux/thin_kiwi.o') )
    self.assertTrue( self.__is_binary('linux/thin_main.o') )
    self.assertTrue( self.__is_binary('linux/thin_program_i386.exe') )
    self.assertTrue( self.__is_binary('linux/thin_program_x86_64.exe') )
    self.assertTrue( self.__is_binary('linux/thin_x86_64_avocado.o') )

  def test_read_magic_thin_dot_o(self):
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/thin_arm64_avocado.o') )
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/thin_armv7_avocado.o') )
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/thin_i386_avocado.o') )
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/thin_x86_64_avocado.o') )

  def test_read_magic_fat_dot_o(self):
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/fat_avocado.o') )
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/fat_all_cherry.o') )
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/fat_32_cherry.o') )
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/fat_64_cherry.o') )

  def test_read_magic_thin_static(self):
    self.assertEqual( None, self.__read_magic('linux/thin_fruits_arm64.a') )
    self.assertEqual( None, self.__read_magic('linux/thin_fruits_armv7.a') )
    self.assertEqual( None, self.__read_magic('linux/thin_fruits_i386.a') )
    self.assertEqual( None, self.__read_magic('linux/thin_fruits_x86_64.a') )

  def test_read_magic_fat_static(self):
    self.assertEqual( None, self.__read_magic('linux/fat_32_fruits.a') )
    self.assertEqual( None, self.__read_magic('linux/fat_64_fruits.a') )
    self.assertEqual( None, self.__read_magic('linux/fat_all_fruits.a') )

  def test_read_magic_thin_exe(self):
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/thin_program_x86_64.exe') )
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/thin_program_i386.exe') )

  def test_read_magic_fat_exe(self):
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/fat_program.exe') )

  def test_read_magic_thin_shared(self):
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/thin_fruits_arm64.so') )
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/thin_fruits_armv7.so') )
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/thin_fruits_i386.so') )
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/thin_fruits_x86_64.so') )

  def test_read_magic_fat_shared(self):
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/fat_all_fruits.so') )
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/fat_32_fruits.so') )
    self.assertEqual( elf.MAGIC_ELF, self.__read_magic('linux/fat_64_fruits.so') )
    
  def test_read_magic_fat_empty_file(self):
    self.assertEqual( None, self.__read_magic('linux/empty.txt') )

  def test_read_magic_fat_small_files(self):
    self.assertEqual( None, self.__read_magic('linux/size1.txt') )
    self.assertEqual( None, self.__read_magic('linux/size2.txt') )
    self.assertEqual( None, self.__read_magic('linux/size3.txt') )
    self.assertEqual( None, self.__read_magic('linux/size4.txt') )
    self.assertEqual( None, self.__read_magic('linux/size5.txt') )
    self.assertEqual( None, self.__read_magic('linux/size6.txt') )
    self.assertEqual( None, self.__read_magic('linux/size7.txt') )

  def test_read_magic_junk_files(self):
    self.assertEqual( None, self.__read_magic('linux/notalib.txt') )

  def __is_binary(self, filename):
    return elf().is_binary(self.data_path(filename))
  
  def __read_magic(self, filename):
    return elf().read_magic(self.data_path(filename))
  
if __name__ == '__main__':
  unit_test.main()
