#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import unittest
import os.path as path

from bes.common import Shell
from bes.fs import file_util, temp_file

class test_rebuild_ar_dot_py(unittest.TestCase):

  TEST_DATA_DIR = path.abspath(path.join(path.dirname(__file__), 'test_data/lipo'))
  SCRIPT = path.abspath(path.normpath(path.join(path.dirname(__file__), '..', 'rebuild_ar.py')))
  
  def extract_fat(self):
    tmp_dir = temp_file.make_temp_dir()
    cmd = [
      self.SCRIPT,
      'x',
      path.join(TEST_DATA_DIR, 'libfat.a'),
    ]
    pass

if __name__ == '__main__':
  unittest.main()
