#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
import os.path as path
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from rebuild.tools import install

class test_install(unit_test):

  def test_install(self):
    tmp_basename = 'foo.sh'
    tmp_src_dir = temp_file.make_temp_dir()
    tmp_filename = path.join(tmp_src_dir, tmp_basename)
    file_util.save(tmp_filename, content = 'this is foo.')
    tmp_dest_dir = temp_file.make_temp_dir()

    install.install(tmp_filename, tmp_dest_dir)

    dest_path = path.join(tmp_dest_dir, tmp_basename)
    self.assertTrue( path.exists(dest_path) )

if __name__ == '__main__':
  unit_test.main()
