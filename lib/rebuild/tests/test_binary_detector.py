#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test
from rebuild import binary_detector

class test_binary_detector(unit_test):

  __unit_test_data_dir__ = 'test_data/binary_objects'

  def test_is_strippable_macos(self):
    self.assertTrue( self.__is_strippable('macos/fat_64_fruits.so') )
    self.assertFalse( self.__is_strippable('macos/thin_fruits_arm64.a') )
    self.assertFalse( self.__is_strippable('macos/notalib.txt') )
    self.assertTrue( self.__is_strippable('macos/thin_program_x86_64.exe') )
    self.assertTrue( self.__is_strippable('macos/fat_program.exe') )
    self.assertTrue( self.__is_strippable('macos/thin_fruits_arm64.so') )
    self.assertFalse( self.__is_strippable('macos/fat_kiwi.o') )
    self.assertFalse( self.__is_strippable('macos/thin_kiwi.o') )
    self.assertFalse( self.__is_strippable('macos/fat_avocado.o') )
    self.assertFalse( self.__is_strippable('macos/thin_cherry.o') )
    self.assertFalse( self.__is_strippable('macos/libarm64.a') )
    self.assertTrue( self.__is_strippable('macos/libarm64.so') )
    self.assertFalse( self.__is_strippable('macos/libarmv7.a') )
    self.assertTrue( self.__is_strippable('macos/libarmv7.so') )
    self.assertFalse( self.__is_strippable('macos/libi386.a') )
    self.assertTrue( self.__is_strippable('macos/libi386.so') )
    self.assertFalse( self.__is_strippable('macos/libx86_64.a') )
    self.assertTrue( self.__is_strippable('macos/libx86_64.so') )

  def test_is_strippable_linux(self):
    self.assertTrue( self.__is_strippable('linux/fat_64_fruits.so') )
    self.assertFalse( self.__is_strippable('linux/thin_fruits_arm64.a') )
    self.assertFalse( self.__is_strippable('linux/notalib.txt') )
    self.assertTrue( self.__is_strippable('linux/thin_program_x86_64.exe') )
    self.assertTrue( self.__is_strippable('linux/fat_program.exe') )
    self.assertTrue( self.__is_strippable('linux/thin_fruits_arm64.so') )
    self.assertFalse( self.__is_strippable('linux/fat_kiwi.o') )
    self.assertFalse( self.__is_strippable('linux/thin_kiwi.o') )
    self.assertFalse( self.__is_strippable('linux/fat_avocado.o') )
    self.assertFalse( self.__is_strippable('linux/thin_cherry.o') )
    self.assertFalse( self.__is_strippable('linux/libarm64.a') )
    self.assertTrue( self.__is_strippable('linux/libarm64.so') )
    self.assertFalse( self.__is_strippable('linux/libarmv7.a') )
    self.assertTrue( self.__is_strippable('linux/libarmv7.so') )
    self.assertFalse( self.__is_strippable('linux/libi386.a') )
    self.assertTrue( self.__is_strippable('linux/libi386.so') )
    self.assertFalse( self.__is_strippable('linux/libx86_64.a') )
    self.assertTrue( self.__is_strippable('linux/libx86_64.so') )
    
  def __is_strippable(self, program_name):
    return binary_detector.is_strippable(self.data_path(program_name))
  
if __name__ == '__main__':
  unit_test.main()
