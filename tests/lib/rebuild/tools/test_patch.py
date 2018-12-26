#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
import os.path as path
from bes.fs import file_util, temp_file
from rebuild.tools import patch

class test_patch(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/tools/patch'

  def test_patch(self):
    p = self.data_path('src_to_dst.patch')
    src = self.data_path('src.txt')
    dst = self.data_path('dst.txt')

    tmp_dir = temp_file.make_temp_dir()
    tmp_src = path.join(tmp_dir, 'src.txt')
    backup_src = tmp_src + '.orig'

    file_util.copy(src, tmp_src)

    patch.patch(p, cwd = tmp_dir, strip = 0, backup = True, posix = True)

    self.assertEqual( file_util.read(dst), file_util.read(tmp_src) )
    self.assertTrue( path.exists(backup_src) )
    self.assertEqual( file_util.read(src), file_util.read(backup_src) )

  def test_patch_compressed(self):
    p = self.data_path('src_to_dst.patch.gz')
    src = self.data_path('src.txt')
    dst = self.data_path('dst.txt')

    tmp_dir = temp_file.make_temp_dir()
    tmp_src = path.join(tmp_dir, 'src.txt')
    backup_src = tmp_src + '.orig'

    file_util.copy(src, tmp_src)

    patch.patch(p, cwd = tmp_dir, strip = 0, backup = True, posix = True)

    self.assertEqual( file_util.read(dst), file_util.read(tmp_src) )
    self.assertTrue( path.exists(backup_src) )
    self.assertEqual( file_util.read(src), file_util.read(backup_src) )
    
  def test_affected_files(self):
    p = self.data_path('src_to_dst.patch')
    actual_affected_files = patch.affected_files(p)
    expected_affected_files = [ 'dst.txt' ]
    self.assertEqual( expected_affected_files, actual_affected_files )

  def test_patch_is_compressed(self):
    self.assertFalse( patch.patch_is_compressed(self.data_path('src_to_dst.patch')) )
    self.assertTrue( patch.patch_is_compressed(self.data_path('src_to_dst.patch.gz')) )
    
if __name__ == '__main__':
  unit_test.main()
