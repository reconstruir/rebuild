#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.testing.unit_test import unit_test
import os.path as path
from bes.system import host
from rebuild.toolchain import ar_replacement
from rebuild.base import build_system
from bes.fs import dir_util, temp_file
from bes.testing.unit_test.unit_test_skip import skip_if

class test_ar_replacement(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/binary_objects'

  IGNORED_CONTENTS = []
  if host.is_macos():
    IGNORED_CONTENTS = set([ '__.SYMDEF' ])
  
  def test_contents_thin(self):
    expected_contents =  [
      'thin_cherry.o',
      'thin_kiwi.o',
    ]
    actual_contents = ar_replacement.contents(self._test_file('thin_fruits_x86_64.a'))
    actual_contents = self._filter_contents(actual_contents)
    self.assertEqual( expected_contents, actual_contents )

  def test_contents_fat(self):
    expected_contents = [
      'fat_64_cherry.o',
      'fat_64_kiwi.o',
    ]
    actual_contents = ar_replacement.contents(self._test_file('fat_64_fruits.a'))
    actual_contents = self._filter_contents(actual_contents)
    self.assertEqual( expected_contents, actual_contents )

  def test_extract_thin(self):
    expected_files = [
      'thin_cherry.o',
      'thin_kiwi.o',
    ]
    tmp_dir = temp_file.make_temp_dir()
    ar_replacement.extract(self._test_file('thin_fruits_x86_64.a'), tmp_dir)
    actual_files = dir_util.list(tmp_dir, relative = True)
    actual_files = self._filter_contents(actual_files)
    self.assertEqual( expected_files, actual_files )

  @skip_if(not host.is_macos(), 'Not osx')
  def test_extract_fat(self):
    expected_files = [
      'arm64_fat_cherry.o',
      'arm64_fat_kiwi.o',
      'armv7_fat_cherry.o',
      'armv7_fat_kiwi.o',
      'i386_fat_cherry.o',
      'i386_fat_kiwi.o',
      'x86_64_fat_cherry.o',
      'x86_64_fat_kiwi.o',
    ]
    tmp_dir = temp_file.make_temp_dir()
    ar_replacement.extract(self._test_file('fat_fruits.a'), tmp_dir)
    actual_files = dir_util.list(tmp_dir, relative = True)
    actual_files = self._filter_contents(actual_files)
    self.assertEqual( expected_files, actual_files )

  def test_replace_thin(self):
    expected_objects = [
      'thin_cherry.o',
      'thin_kiwi.o',
    ]
    tmp_dir = temp_file.make_temp_dir()
    tmp_archive = path.join(tmp_dir, 'thin_fruits.a')
    objects = [ self._test_file(o) for o in expected_objects ]
    ar_replacement.replace(tmp_archive, objects)
    actual_objects = ar_replacement.contents(tmp_archive)
    actual_objects = self._filter_contents(actual_objects)
    self.assertEqual( expected_objects, actual_objects )

  def test_replace_fat(self):
    expected_objects = [
      'fat_cherry.o',
      'fat_kiwi.o',
    ]
    tmp_dir = temp_file.make_temp_dir()
    tmp_archive = path.join(tmp_dir, 'fat_fruits.a')
    objects = [ self._test_file(o) for o in expected_objects ]
    ar_replacement.replace(tmp_archive, objects)
    actual_objects = ar_replacement.contents(tmp_archive)
    actual_objects = self._filter_contents(actual_objects)
    self.assertEqual( expected_objects, actual_objects )

  def test_replace_add_thin(self):
    expected_objects = [
      'thin_cherry.o',
      'thin_kiwi.o',
    ]
    tmp_dir = temp_file.make_temp_dir()
    tmp_archive = path.join(tmp_dir, 'thin_fruits.a')
    objects = [ self._test_file(o) for o in expected_objects ]
    ar_replacement.replace(tmp_archive, objects)
    actual_objects = ar_replacement.contents(tmp_archive)
    actual_objects = self._filter_contents(actual_objects)
    self.assertEqual( expected_objects, actual_objects )
    expected_objects = [
      'thin_cherry.o',
      'thin_kiwi.o',
      'thin_x86_64_avocado.o',
    ]
    objects = [ self._test_file(o) for o in [ 'thin_x86_64_avocado.o' ] ]
    ar_replacement.replace(tmp_archive, objects)
    actual_objects = ar_replacement.contents(tmp_archive)
    actual_objects = self._filter_contents(actual_objects)
    self.assertEqual( expected_objects, actual_objects )

  def _test_file(self, filename):
    return self.platform_data_path(filename)

  @classmethod
  def _filter_contents(clazz, contents):
    def _include(c):
      for ignored in clazz.IGNORED_CONTENTS:
        if c.find(ignored) >= 0:
          return False
      return True
    return [ c for c in contents if _include(c) ]
    
if __name__ == '__main__':
  unit_test.main()
