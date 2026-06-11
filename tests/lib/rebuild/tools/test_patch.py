#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
import os.path as path
from bes.files.bf_file_ops import bf_file_ops
from bes.files.bf_temp_file import bf_temp_file
from rebuild.tools.patch import patch

class test_patch(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/tools/patch'

  def test_patch(self):
    p = self.data_path('src_to_dst.patch')
    src = self.data_path('src.txt')
    dst = self.data_path('dst.txt')

    tmp_dir = bf_temp_file.make_temp_dir()
    tmp_src = path.join(tmp_dir, 'src.txt')
    backup_src = tmp_src + '.orig'

    bf_file_ops.copy(src, tmp_src)

    patch.patch(p, cwd = tmp_dir, strip = 0, backup = True, posix = True)

    self.assertEqual( bf_file_ops.read(dst), bf_file_ops.read(tmp_src) )
    self.assertTrue( path.exists(backup_src) )
    self.assertEqual( bf_file_ops.read(src), bf_file_ops.read(backup_src) )

  def test_patch_compressed(self):
    p = self.data_path('src_to_dst.patch.gz')
    src = self.data_path('src.txt')
    dst = self.data_path('dst.txt')

    tmp_dir = bf_temp_file.make_temp_dir()
    tmp_src = path.join(tmp_dir, 'src.txt')
    backup_src = tmp_src + '.orig'

    bf_file_ops.copy(src, tmp_src)

    patch.patch(p, cwd = tmp_dir, strip = 0, backup = True, posix = True)

    self.assertEqual( bf_file_ops.read(dst), bf_file_ops.read(tmp_src) )
    self.assertTrue( path.exists(backup_src) )
    self.assertEqual( bf_file_ops.read(src), bf_file_ops.read(backup_src) )
    
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
