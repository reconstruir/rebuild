#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest
from bes.fs import file_util, temp_file
from rebuild import Install

class TestInstall(unittest.TestCase):

  def test_install(self):
    tmp_basename = 'foo.sh'
    tmp_src_dir = temp_file.make_temp_dir()
    tmp_filename = path.join(tmp_src_dir, tmp_basename)
    file_util.save(tmp_filename, content = 'this is foo.')
    tmp_dest_dir = temp_file.make_temp_dir()

    Install.install(tmp_filename, tmp_dest_dir)

    dest_path = path.join(tmp_dest_dir, tmp_basename)
    self.assertTrue( path.exists(dest_path) )

if __name__ == '__main__':
  unittest.main()
