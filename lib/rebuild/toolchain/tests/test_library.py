#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.toolchain import library
from bes.testing.unit_test.unit_test_skip import skip_if
from bes.system import host

class test_library(unit_test):

  __unit_test_data_dir__ = '../../../../test_data/binary_objects'

  def test_is_library(self):
    self.assertFalse( self.__is_library('cherry.o') )
    self.assertFalse( self.__is_library('empty.txt') )
    self.assertFalse( self.__is_library('fat_32_cherry.o') )
    self.assertTrue( self.__is_library('fat_32_fruits.a') )
    self.assertTrue( self.__is_library('fat_32_fruits.so') )
    self.assertFalse( self.__is_library('fat_32_kiwi.o') )
    self.assertFalse( self.__is_library('fat_64_cherry.o') )
    self.assertTrue( self.__is_library('fat_64_fruits.a') )
    self.assertTrue( self.__is_library('fat_64_fruits.so') )
    self.assertFalse( self.__is_library('fat_64_kiwi.o') )
    self.assertFalse( self.__is_library('fat_all_cherry.o') )
    self.assertTrue( self.__is_library('fat_all_fruits.a') )
    self.assertTrue( self.__is_library('fat_all_fruits.so') )
    self.assertFalse( self.__is_library('fat_all_kiwi.o') )
    self.assertFalse( self.__is_library('fat_avocado.o') )
    self.assertFalse( self.__is_library('fat_cherry.o') )
    self.assertTrue( self.__is_library('fat_all_fruits.a') )
    self.assertFalse( self.__is_library('fat_kiwi.o') )
    self.assertFalse( self.__is_library('fat_main.o') )
    self.assertFalse( self.__is_library('fat_program.exe') )
    self.assertFalse( self.__is_library('kiwi.o') )
    self.assertTrue( self.__is_library('libarm64.a') )
    self.assertTrue( self.__is_library('libarm64.so') )
    self.assertTrue( self.__is_library('libarmv7.a') )
    self.assertTrue( self.__is_library('libarmv7.so') )
    self.assertTrue( self.__is_library('libi386.a') )
    self.assertTrue( self.__is_library('libi386.so') )
    self.assertTrue( self.__is_library('libx86_64.a') )
    self.assertTrue( self.__is_library('libx86_64.so') )
    self.assertFalse( self.__is_library('notalib.txt') )
    self.assertFalse( self.__is_library('size1.txt') )
    self.assertFalse( self.__is_library('size10.txt') )
    self.assertFalse( self.__is_library('size2.txt') )
    self.assertFalse( self.__is_library('size3.txt') )
    self.assertFalse( self.__is_library('size4.txt') )
    self.assertFalse( self.__is_library('size5.txt') )
    self.assertFalse( self.__is_library('size6.txt') )
    self.assertFalse( self.__is_library('size7.txt') )
    self.assertFalse( self.__is_library('size8.txt') )
    self.assertFalse( self.__is_library('size9.txt') )
    self.assertFalse( self.__is_library('thin_arm64_avocado.o') )
    self.assertFalse( self.__is_library('thin_armv7_avocado.o') )
    self.assertFalse( self.__is_library('thin_cherry.o') )
    self.assertTrue( self.__is_library('thin_fruits_arm64.a') )
    self.assertTrue( self.__is_library('thin_fruits_arm64.so') )
    self.assertTrue( self.__is_library('thin_fruits_armv7.a') )
    self.assertTrue( self.__is_library('thin_fruits_armv7.so') )
    self.assertTrue( self.__is_library('thin_fruits_i386.a') )
    self.assertTrue( self.__is_library('thin_fruits_i386.so') )
    self.assertTrue( self.__is_library('thin_fruits_x86_64.a') )
    self.assertTrue( self.__is_library('thin_fruits_x86_64.so') )
    self.assertFalse( self.__is_library('thin_i386_avocado.o') )
    self.assertFalse( self.__is_library('thin_kiwi.o') )
    self.assertFalse( self.__is_library('thin_main.o') )
    self.assertFalse( self.__is_library('thin_program_i386.exe') )
    self.assertFalse( self.__is_library('thin_program_x86_64.exe') )
    self.assertFalse( self.__is_library('thin_x86_64_avocado.o') )

  def test_is_shared_library(self):
    self.assertFalse( self.__is_shared_library('cherry.o') )
    self.assertFalse( self.__is_shared_library('empty.txt') )
    self.assertFalse( self.__is_shared_library('fat_32_cherry.o') )
    self.assertFalse( self.__is_shared_library('fat_32_fruits.a') )
    self.assertTrue( self.__is_shared_library('fat_32_fruits.so') )
    self.assertFalse( self.__is_shared_library('fat_32_kiwi.o') )
    self.assertFalse( self.__is_shared_library('fat_64_cherry.o') )
    self.assertFalse( self.__is_shared_library('fat_64_fruits.a') )
    self.assertTrue( self.__is_shared_library('fat_64_fruits.so') )
    self.assertFalse( self.__is_shared_library('fat_64_kiwi.o') )
    self.assertFalse( self.__is_shared_library('fat_all_cherry.o') )
    self.assertFalse( self.__is_shared_library('fat_all_fruits.a') )
    self.assertTrue( self.__is_shared_library('fat_all_fruits.so') )
    self.assertFalse( self.__is_shared_library('fat_all_kiwi.o') )
    self.assertFalse( self.__is_shared_library('fat_avocado.o') )
    self.assertFalse( self.__is_shared_library('fat_cherry.o') )
    self.assertFalse( self.__is_shared_library('fat_all_fruits.a') )
    self.assertFalse( self.__is_shared_library('fat_kiwi.o') )
    self.assertFalse( self.__is_shared_library('fat_main.o') )
    self.assertFalse( self.__is_shared_library('fat_program.exe') )
    self.assertFalse( self.__is_shared_library('kiwi.o') )
    self.assertFalse( self.__is_shared_library('libarm64.a') )
    self.assertTrue( self.__is_shared_library('libarm64.so') )
    self.assertFalse( self.__is_shared_library('libarmv7.a') )
    self.assertTrue( self.__is_shared_library('libarmv7.so') )
    self.assertFalse( self.__is_shared_library('libi386.a') )
    self.assertTrue( self.__is_shared_library('libi386.so') )
    self.assertFalse( self.__is_shared_library('libx86_64.a') )
    self.assertTrue( self.__is_shared_library('libx86_64.so') )
    self.assertFalse( self.__is_shared_library('notalib.txt') )
    self.assertFalse( self.__is_shared_library('size1.txt') )
    self.assertFalse( self.__is_shared_library('size10.txt') )
    self.assertFalse( self.__is_shared_library('size2.txt') )
    self.assertFalse( self.__is_shared_library('size3.txt') )
    self.assertFalse( self.__is_shared_library('size4.txt') )
    self.assertFalse( self.__is_shared_library('size5.txt') )
    self.assertFalse( self.__is_shared_library('size6.txt') )
    self.assertFalse( self.__is_shared_library('size7.txt') )
    self.assertFalse( self.__is_shared_library('size8.txt') )
    self.assertFalse( self.__is_shared_library('size9.txt') )
    self.assertFalse( self.__is_shared_library('thin_arm64_avocado.o') )
    self.assertFalse( self.__is_shared_library('thin_armv7_avocado.o') )
    self.assertFalse( self.__is_shared_library('thin_cherry.o') )
    self.assertFalse( self.__is_shared_library('thin_fruits_arm64.a') )
    self.assertTrue( self.__is_shared_library('thin_fruits_arm64.so') )
    self.assertFalse( self.__is_shared_library('thin_fruits_armv7.a') )
    self.assertTrue( self.__is_shared_library('thin_fruits_armv7.so') )
    self.assertFalse( self.__is_shared_library('thin_fruits_i386.a') )
    self.assertTrue( self.__is_shared_library('thin_fruits_i386.so') )
    self.assertFalse( self.__is_shared_library('thin_fruits_x86_64.a') )
    self.assertTrue( self.__is_shared_library('thin_fruits_x86_64.so') )
    self.assertFalse( self.__is_shared_library('thin_i386_avocado.o') )
    self.assertFalse( self.__is_shared_library('thin_kiwi.o') )
    self.assertFalse( self.__is_shared_library('thin_main.o') )
    self.assertFalse( self.__is_shared_library('thin_program_i386.exe') )
    self.assertFalse( self.__is_shared_library('thin_program_x86_64.exe') )
    self.assertFalse( self.__is_shared_library('thin_x86_64_avocado.o') )

  @skip_if(not host.is_macos(), 'not macos')
  def test_dependencies_macos(self):
    deps = library.dependencies('/bin/bash')
    self.assertEquals( 2, len(deps) )
    self.assertTrue( path.basename(deps[0]).startswith('libSystem') )
    self.assertTrue( path.basename(deps[1]).startswith('libncurses') )
    
  @skip_if(not host.is_linux(), 'not linux')
  def test_dependencies_linux(self):
    deps = library.dependencies('/bin/bash')
    if host.DISTRO == host.RASPBIAN:
      expected_deps = [
        '/lib/arm-linux-gnueabihf/libc.so.6',
        '/lib/arm-linux-gnueabihf/libdl.so.2',
        '/lib/arm-linux-gnueabihf/libncurses.so.5',
        '/lib/arm-linux-gnueabihf/libtinfo.so.5',
        '/lib/ld-linux-armhf.so.3',
        '/usr/lib/arm-linux-gnueabihf/libarmmem.so',
      ]
    else:
      expected_deps = [
        '/lib/x86_64-linux-gnu/libc.so.6',
        '/lib/x86_64-linux-gnu/libdl.so.2',
        '/lib/x86_64-linux-gnu/libtinfo.so.5',
        '/lib64/ld-linux-x86-64.so.2',
      ]
      
    self.assertEquals( expected_deps, deps )
    
  def __is_library(self, filename):
    return library.is_library(self.data_path(filename, platform_specific = True))

  def __is_shared_library(self, filename):
    return library.is_shared_library(self.data_path(filename, platform_specific = True))

  def __is_static_library(self, filename):
    return library.is_static_library(self.data_path(filename, platform_specific = True))

  def test_is_archive_dir_error(self):
    self.assertFalse( library.is_archive('/usr/bin') )
    
  def test_name(self):
    self.assertEqual( 'foo', library.name('/usr/lib/libfoo.1.2.3.dylib') )
    self.assertEqual( 'foo', library.name('/usr/lib/libfoo.1.2.dylib') )
    self.assertEqual( 'foo', library.name('/usr/lib/libfoo.1.dylib') )
    self.assertEqual( 'foo', library.name('/usr/lib/libfoo.dylib') )
    self.assertEqual( 'foo', library.name('libfoo.dylib') )
    self.assertEqual( 'foo', library.name('/usr/lib/libfoo.so.1.2.3') )
    self.assertEqual( 'foo', library.name('/usr/lib/libfoo.so.1.2') )
    self.assertEqual( 'foo', library.name('/usr/lib/libfoo.so.1') )
    self.assertEqual( 'foo', library.name('/usr/lib/libfoo.so') )
    self.assertEqual( 'foo', library.name('libfoo.dylib') )
    self.assertEqual( 'foo', library.name('libfoo.a') )
    self.assertEqual( 'foo', library.name('libfoo.1.2.8.dylib') )
    self.assertEqual( 'foo', library.name('libfoo.1.dylib') )
    self.assertEqual( 'foo', library.name('libfoo.dylib') )
    
  def test_name_add_prefix(self):
    self.assertEqual( 'libkiwi_foo.a', library.name_add_prefix('libfoo.a', 'kiwi_') )
    self.assertEqual( 'libkiwi_foo.dylib', library.name_add_prefix('libfoo.dylib', 'kiwi_') )
    self.assertEqual( 'libkiwi_foo.1.2.3.dylib', library.name_add_prefix('libfoo.1.2.3.dylib', 'kiwi_') )
    self.assertEqual( 'libkiwi_foo.so', library.name_add_prefix('libfoo.so', 'kiwi_') )
    self.assertEqual( 'libkiwi_foo.so.1', library.name_add_prefix('libfoo.so.1', 'kiwi_') )
    self.assertEqual( None, library.name_add_prefix('pic.png', 'kiwi_') )

  @skip_if(not host.is_macos(), 'not macos')
  def test_list_libraries_macos(self):
    expected_libs = [
      'fat_32_fruits.a',
      'fat_32_fruits.so',
      'fat_64_fruits.a',
      'fat_64_fruits.so',
      'fat_all_fruits.a',
      'fat_all_fruits.so',
      'fat_fruits.a',
      'fat_fruits.so',
      'libarm64.a',
      'libarm64.so',
      'libarmv7.a',
      'libarmv7.so',
      'libi386.a',
      'libi386.so',
      'libx86_64.a',
      'libx86_64.so',
      'thin_fruits_arm64.a',
      'thin_fruits_arm64.so',
      'thin_fruits_armv7.a',
      'thin_fruits_armv7.so',
      'thin_fruits_i386.a',
      'thin_fruits_i386.so',
      'thin_fruits_x86_64.a',
      'thin_fruits_x86_64.so',
    ]
    self.assertEqual( expected_libs, library.list_libraries(self.data_dir(platform_specific = True), relative = True) )

  @skip_if(not host.is_linux(), 'not linux')
  def test_list_libraries_macos(self):
    self.maxDiff = None
    expected_libs = [
      'fat_32_fruits.a',
      'fat_32_fruits.so',
      'fat_64_fruits.a',
      'fat_64_fruits.so',
      'fat_all_fruits.a',
      'fat_all_fruits.so',
      'libarm64.a',
      'libarm64.so',
      'libarmv7.a',
      'libarmv7.so',
      'libi386.a',
      'libi386.so',
      'libx86_64.a',
      'libx86_64.so',
      'thin_fruits_arm64.a',
      'thin_fruits_arm64.so',
      'thin_fruits_armv7.a',
      'thin_fruits_armv7.so',
      'thin_fruits_i386.a',
      'thin_fruits_i386.so',
      'thin_fruits_x86_64.a',
      'thin_fruits_x86_64.so',
    ]
    self.assertEqual( expected_libs, library.list_libraries(self.data_dir(platform_specific = True)) )

  def test_relative_rpath(self):
    self.assertEqual( '../lib/libx.so', library.relative_rpath('/foo/bar/bin/pngfix', '/foo/bar/lib/libx.so') )
    self.assertEqual( '', library.relative_rpath('/foo/bar/lib/liby.so', '/foo/bar/lib/libx.so') )

if __name__ == '__main__':
  unit_test.main()
