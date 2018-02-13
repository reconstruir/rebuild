#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.testing.unit_test import unit_test
from rebuild.source_finder import tarball_finder

class test_tarball_finder(unit_test):

  TEST_FILENAMES = [
    'libfoo-1.2.3.tar.gz',
    'libbar-1.2.3.tar.gz',
    'libbaz-1.2.3-4.tar.gz',
    'subprocess32-3.2.6.tar.gz',
    'macos/my-something-macos.zip',
    'linux/my-something-linux.zip',
  ]

  def test_find_in_list(self):
    self.assertEqual( [ 'libfoo-1.2.3.tar.gz' ], tarball_finder.find_in_list(self.TEST_FILENAMES, 'libfoo', '1.2.3') )
    self.assertEqual( [ 'libfoo-1.2.3.tar.gz' ], tarball_finder.find_in_list(self.TEST_FILENAMES, 'foo', '1.2.3') )

  def test_find_in_list_dash(self):
    self.assertEqual( [ 'libbaz-1.2.3-4.tar.gz' ], tarball_finder.find_in_list(self.TEST_FILENAMES, 'libbaz', '1.2.3.4') )
    self.assertEqual( [ 'libbaz-1.2.3-4.tar.gz' ], tarball_finder.find_in_list(self.TEST_FILENAMES, 'libbaz', '1.2.3-4') )
    self.assertEqual( [ 'libbaz-1.2.3-4.tar.gz' ], tarball_finder.find_in_list(self.TEST_FILENAMES, 'baz', '1.2.3.4') )

  def test_find_in_list_python(self):
    self.assertEqual( [ 'subprocess32-3.2.6.tar.gz' ], tarball_finder.find_in_list(self.TEST_FILENAMES, 'python_subprocess32', '3.2.6') )

  def test_find_no_version(self):
    self.assertEqual( [ 'linux/my-something-linux.zip', 'macos/my-something-macos.zip' ], tarball_finder.find_in_list(self.TEST_FILENAMES, 'my-something', '') )

if __name__ == '__main__':
  unit_test.main()
