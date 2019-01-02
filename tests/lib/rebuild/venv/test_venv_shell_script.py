#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file

from rebuild.venv.venv_shell_script import venv_shell_script

class test_venv_shell_script(unit_test):

  def test_save_executable(self):
    template = '#!/bin/bash\necho @FOO@ @BAR@'
    basename = 'foo.sh'
    script = venv_shell_script(template, basename)
    tmp_root_dir = temp_file.make_temp_dir()
    variables = {
      '@FOO@': 'foo',
      '@BAR@': 'bar',
    }
    save_rv = script.save(tmp_root_dir, variables)
    tmp_filename = path.join(tmp_root_dir, basename)
    self.assertTrue( path.exists(tmp_filename) )
    content = file_util.read(tmp_filename, 'utf-8')
    expected_content = '#!/bin/bash\necho foo bar'
    self.assertEqual( expected_content, content )
    self.assertEqual( file_util.mode(tmp_filename), 0o755 )
    
  def test_save_not_executable(self):
    template = 'something @FOO@ and @BAR@'
    basename = 'foo.sh'
    script = venv_shell_script(template, basename)
    tmp_root_dir = temp_file.make_temp_dir()
    variables = {
      '@FOO@': 'foo',
      '@BAR@': 'bar',
    }
    save_rv = script.save(tmp_root_dir, variables)
    tmp_filename = path.join(tmp_root_dir, basename)
    self.assertTrue( path.exists(tmp_filename) )
    content = file_util.read(tmp_filename, 'utf-8')
    expected_content = 'something foo and bar'
    self.assertEqual( expected_content, content )
    self.assertEqual( file_util.mode(tmp_filename), 0o644 )
    self.assertEqual( True, save_rv )
    
if __name__ == '__main__':
  unit_test.main()
