#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild import binary_detector

class test_binary_detector(unit_test):

  __unit_test_data_dir__ = 'test_data/binary_objects'

  def test_is_strippable_macho(self):
    self.assertTrue( self._is_strippable('macos/fat_64_fruits.so') )
    self.assertFalse( self._is_strippable('macos/thin_fruits_arm64.a') )
    self.assertFalse( self._is_strippable('macos/notalib.txt') )
    self.assertTrue( self._is_strippable('macos/thin_program_x86_64.exe') )
    self.assertTrue( self._is_strippable('macos/fat_program.exe') )
    self.assertTrue( self._is_strippable('macos/thin_fruits_arm64.so') )
    self.assertFalse( self._is_strippable('macos/fat_kiwi.o') )
    self.assertFalse( self._is_strippable('macos/thin_kiwi.o') )
    self.assertFalse( self._is_strippable('macos/fat_avocado.o') )
    self.assertFalse( self._is_strippable('macos/thin_cherry.o') )
    self.assertFalse( self._is_strippable('macos/libarm64.a') )
    self.assertTrue( self._is_strippable('macos/libarm64.so') )
    self.assertFalse( self._is_strippable('macos/libarmv7.a') )
    self.assertTrue( self._is_strippable('macos/libarmv7.so') )
    self.assertFalse( self._is_strippable('macos/libi386.a') )
    self.assertTrue( self._is_strippable('macos/libi386.so') )
    self.assertFalse( self._is_strippable('macos/libx86_64.a') )
    self.assertTrue( self._is_strippable('macos/libx86_64.so') )

  def test_is_strippable_elf(self):
    self.assertTrue( self._is_strippable('linux/fat_64_fruits.so') )
    self.assertFalse( self._is_strippable('linux/thin_fruits_arm64.a') )
    self.assertFalse( self._is_strippable('linux/notalib.txt') )
    self.assertTrue( self._is_strippable('linux/thin_program_x86_64.exe') )
    self.assertTrue( self._is_strippable('linux/fat_program.exe') )
    self.assertTrue( self._is_strippable('linux/thin_fruits_arm64.so') )
    self.assertFalse( self._is_strippable('linux/fat_kiwi.o') )
    self.assertFalse( self._is_strippable('linux/thin_kiwi.o') )
    self.assertFalse( self._is_strippable('linux/fat_avocado.o') )
    self.assertFalse( self._is_strippable('linux/thin_cherry.o') )
    self.assertFalse( self._is_strippable('linux/libarm64.a') )
    self.assertTrue( self._is_strippable('linux/libarm64.so') )
    self.assertFalse( self._is_strippable('linux/libarmv7.a') )
    self.assertTrue( self._is_strippable('linux/libarmv7.so') )
    self.assertFalse( self._is_strippable('linux/libi386.a') )
    self.assertTrue( self._is_strippable('linux/libi386.so') )
    self.assertFalse( self._is_strippable('linux/libx86_64.a') )
    self.assertTrue( self._is_strippable('linux/libx86_64.so') )
    
  def test_is_strippable_format_name(self):
    self.assertTrue( self._is_strippable('linux/fat_64_fruits.so', format_name = 'elf') )
    self.assertFalse( self._is_strippable('linux/fat_64_fruits.so', format_name = 'macho') )
    self.assertTrue( self._is_strippable('macos/fat_64_fruits.so', format_name = 'macho') )
    self.assertFalse( self._is_strippable('macos/fat_64_fruits.so', format_name = 'elf') )
  
  def _is_strippable(self, program_name, format_name = None):
    return binary_detector.is_strippable(self.data_path(program_name), format_name = format_name)

if __name__ == '__main__':
  unit_test.main()
