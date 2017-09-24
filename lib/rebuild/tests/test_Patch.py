#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest
from bes.fs import file_util, temp_file
from rebuild import Patch

class TestPatch(unittest.TestCase):

  TEST_DATA_DIR = path.abspath(path.join(path.dirname(__file__), 'test_data/patch'))

  def test_patch(self):
    patch = path.join(self.TEST_DATA_DIR, 'src_to_dst.patch')
    src = path.join(self.TEST_DATA_DIR, 'src.txt')
    dst = path.join(self.TEST_DATA_DIR, 'dst.txt')

    tmp_dir = temp_file.make_temp_dir()
    tmp_src = path.join(tmp_dir, 'src.txt')
    backup_src = tmp_src + '.orig'

    file_util.copy(src, tmp_src)

    Patch.patch(patch, cwd = tmp_dir, strip = 0, backup = True, posix = True)

    self.assertEqual( file_util.read(dst), file_util.read(tmp_src) )
    self.assertTrue( path.exists(backup_src) )
    self.assertEqual( file_util.read(src), file_util.read(backup_src) )

  def test_affected_files(self):
    patch = path.join(self.TEST_DATA_DIR, 'src_to_dst.patch')
    actual_affected_files = Patch.affected_files(patch)
    expected_affected_files = [ 'dst.txt' ]
    self.assertEqual( expected_affected_files, actual_affected_files )

if __name__ == '__main__':
  unittest.main()
