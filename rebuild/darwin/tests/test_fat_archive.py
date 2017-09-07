#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path
from bes.fs import file_checksum, file_util, temp_file
from bes.archive import archiver, archive_extension, temp_archive
from rebuild.darwin import fat_archive, Lipo
from bes.system import host
from bes.unit_test.unit_test_skip import raise_skip_if_not_platform
from bes.unit_test import unit_test

class test_darwin_package_util(unit_test):

  __unit_test_data_dir__ = 'test_data/binary_objects'

  DEBUG = False
  #DEBUG = True

  @classmethod
  def setUpClass(clazz):
    raise_skip_if_not_platform(host.MACOS)

  def test_thin_to_fat_static(self):
    other_items = [
      temp_archive.Item('foo.txt', content = 'foo.txt\n'),
      temp_archive.Item('bar.txt', content = 'bar.txt\n'),
    ]

    i386_archive = self.__make_test_archive('lib/libsomething.a', 'i386', other_items)
    x86_64_archive = self.__make_test_archive('lib/libsomething.a', 'x86_64', other_items)
    armv7_archive = self.__make_test_archive('lib/libsomething.a', 'armv7', other_items)
    self.assertEqual( [ 'i386' ], Lipo.archs(self.__test_file('libi386.a') ) )
    self.assertEqual( [ 'x86_64' ], Lipo.archs(self.__test_file('libx86_64.a') ) )
    self.assertEqual( [ 'armv7' ], Lipo.archs(self.__test_file('libarmv7.a') ) )

    thin_packages = [
      i386_archive.filename,
      x86_64_archive.filename,
      armv7_archive.filename,
    ]
    tmp_dir = temp_file.make_temp_dir()
    fat_package = path.join(tmp_dir, 'fat.tgz')
    fat_archive.thin_to_fat(thin_packages, fat_package)
    self.assertTrue( archiver.is_valid(fat_package) )

    tmp_extract_dir = temp_file.make_temp_dir()
    archiver.extract(fat_package, tmp_extract_dir)

    fat_library = path.join(tmp_extract_dir, 'lib/libsomething.a')
    self.assertTrue( path.isfile(path.join(tmp_extract_dir, 'foo.txt')) )
    self.assertTrue( path.isfile(path.join(tmp_extract_dir, 'bar.txt')) )
    
    self.assertTrue( path.isfile(fat_library) )
    self.assertEqual( ['armv7', 'i386', 'x86_64'], Lipo.archs(fat_library) )
    
  def test_thin_to_fat_bad_normals_checksums(self):
    i386_other_items = [
      temp_archive.Item('foo.txt', content = 'i386 foo.txt\n'),
      temp_archive.Item('bar.txt', content = 'i386 bar.txt\n'),
    ]
    i386_archive = self.__make_test_archive('lib/libsomething.a', 'i386', i386_other_items)
    x86_64_other_items = [
      temp_archive.Item('foo.txt', content = 'x86_64 foo.txt\n'),
      temp_archive.Item('bar.txt', content = 'x86_64 bar.txt\n'),
    ]
    x86_64_archive = self.__make_test_archive('lib/libsomething.a', 'x86_64', x86_64_other_items)
    armv7_other_items = [
      temp_archive.Item('foo.txt', content = 'armv7 foo.txt\n'),
      temp_archive.Item('bar.txt', content = 'armv7 bar.txt\n'),
    ]
    armv7_archive = self.__make_test_archive('lib/libsomething.a', 'armv7', armv7_other_items)

    thin_packages = [
      i386_archive.filename,
      x86_64_archive.filename,
      armv7_archive.filename,
    ]
    tmp_dir = temp_file.make_temp_dir()
    fat_package = path.join(tmp_dir, 'fat.tgz')

    with self.assertRaises(RuntimeError) as context:
      fat_archive.thin_to_fat(thin_packages, fat_package)
      self.assertTrue( archiver.is_valid(fat_package) )
    
  def __test_file(self, filename):
    return self.data_path(filename, platform_specific = True)
      
  def __make_test_archive(self, target, arch, other_items):
    items = [
      temp_archive.Item(target, filename = self.__test_file('lib%s.a' % (arch))),
    ]
    return temp_archive.make_temp_archive(items + other_items, archive_extension.TGZ, prefix = '%s_' % (arch), delete = not self.DEBUG)
  
if __name__ == '__main__':
  unit_test.main()
