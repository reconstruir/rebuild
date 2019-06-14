#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os, os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.file_copy import file_copy
from bes.fs.temp_file import temp_file
from rebuild.jail.sync import sync

class test_sync(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/sync'

  DEBUG = False
  #DEBUG = True

  def test_sync(self):
    tmp_dst_dir = temp_file.make_temp_dir(delete = not self.DEBUG)

    files = [
      'files',
      'files/1',
      'files/1/2',
      'files/1/2/3',
      'files/1/2/3/4',
      'files/1/2/3/4/5',
      'files/1/2/3/4/5/apple.txt',
      'files/1/2/3/4/5/kiwi.txt',
      'files/bar.txt',
      'files/empty',
      'files/foo.txt',
      'files/kiwi_link.txt',
    ]

    src_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    file_copy.copy_tree(self.data_dir(), src_dir)
    
    num_links_before = self.num_links(src_dir)

    sync.sync_files(src_dir, tmp_dst_dir, files, 'foo')
    
    actual_files = file_find.find(tmp_dst_dir, file_type = file_find.ANY)
    self.assertEqual( actual_files, files )

    num_links_after = self.num_links(src_dir)
    self.assertEqual( num_links_before, [ n  - 1 for n in num_links_after ] )

  @classmethod
  def num_links(clazz, d):
    files = file_find.find(d, relative = False, file_type = file_find.FILE)
    return [ os.stat(f).st_nlink for f in files ]
    
if __name__ == '__main__':
  unit_test.main()
