#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file

from rebuild.packager import rebuild_manager_script

class test_rebuild_manager_script(unit_test):

  def test_save_executable(self):
    template = '#!/bin/bash\necho @FOO@ @BAR@'
    basename = 'foo.sh'
    script = rebuild_manager_script(template, basename)
    tmp_root_dir = temp_file.make_temp_dir()
    variables = {
      '@FOO@': 'foo',
      '@BAR@': 'bar',
    }
    save_rv = script.save(tmp_root_dir, variables)
    tmp_filename = path.join(tmp_root_dir, basename)
    self.assertTrue( path.exists(tmp_filename) )
    content = file_util.read(tmp_filename)
    expected_content = '#!/bin/bash\necho foo bar'
    self.assertEqual( expected_content, content )
    self.assertEqual( file_util.mode(tmp_filename), 0755 )
    
  def test_save_not_executable(self):
    template = 'something @FOO@ and @BAR@'
    basename = 'foo.sh'
    script = rebuild_manager_script(template, basename)
    tmp_root_dir = temp_file.make_temp_dir()
    variables = {
      '@FOO@': 'foo',
      '@BAR@': 'bar',
    }
    save_rv = script.save(tmp_root_dir, variables)
    tmp_filename = path.join(tmp_root_dir, basename)
    self.assertTrue( path.exists(tmp_filename) )
    content = file_util.read(tmp_filename)
    expected_content = 'something foo and bar'
    self.assertEqual( expected_content, content )
    self.assertEqual( file_util.mode(tmp_filename), 0644 )
    self.assertEqual( True, save_rv )
    
if __name__ == '__main__':
  unit_test.main()
