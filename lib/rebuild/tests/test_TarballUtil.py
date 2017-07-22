#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from rebuild import TarballUtil

class TestTarballUtil(unittest.TestCase):

  TEST_FILENAMES = [
    'libfoo-1.2.3.tar.gz',
    'libbar-1.2.3.tar.gz',
    'libbaz-1.2.3-4.tar.gz',
    'subprocess32-3.2.6.tar.gz',
  ]

  def test_find_in_list(self):
    self.assertEqual( [ 'libfoo-1.2.3.tar.gz' ], TarballUtil.find_in_list(self.TEST_FILENAMES, 'libfoo', '1.2.3') )
    self.assertEqual( [ 'libfoo-1.2.3.tar.gz' ], TarballUtil.find_in_list(self.TEST_FILENAMES, 'foo', '1.2.3') )

  def test_find_in_list_dash(self):
    self.assertEqual( [ 'libbaz-1.2.3-4.tar.gz' ], TarballUtil.find_in_list(self.TEST_FILENAMES, 'libbaz', '1.2.3.4') )
    self.assertEqual( [ 'libbaz-1.2.3-4.tar.gz' ], TarballUtil.find_in_list(self.TEST_FILENAMES, 'libbaz', '1.2.3-4') )
    self.assertEqual( [ 'libbaz-1.2.3-4.tar.gz' ], TarballUtil.find_in_list(self.TEST_FILENAMES, 'baz', '1.2.3.4') )

  def test_find_in_list_python(self):
    self.assertEqual( [ 'subprocess32-3.2.6.tar.gz' ], TarballUtil.find_in_list(self.TEST_FILENAMES, 'python_subprocess32', '3.2.6') )

if __name__ == '__main__':
  unittest.main()
