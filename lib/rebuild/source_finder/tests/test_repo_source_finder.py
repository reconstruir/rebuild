#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.testing import temp_content
from bes.fs import temp_file
from bes.git import repo
from rebuild.source_finder import repo_source_finder
import os.path as path

from test_local_source_finder import source_dir_maker

class test_repo_source_finder(unit_test):

  def test_repo_source_finder_tar_gz(self):
    tmp_source_repo_dir = self._make_git_repo([
      'file a/alpha-1.2.3.tar.gz "${tarball}" 644',
      'file b/beta-1.2.3.tar.gz "${tarball}" 644',
    ])
    tmp_repo_dir = temp_file.make_temp_dir()
    finder = repo_source_finder(tmp_repo_dir, tmp_source_repo_dir)
    self.assertEqual( path.join(tmp_repo_dir, 'a/alpha-1.2.3.tar.gz'),
                      finder.find_source('alpha', '1.2.3', 'linux') )

  @classmethod
  def _make_git_repo(clazz, items):
    tmp_source_dir = source_dir_maker.make(items)
    r = repo(tmp_source_dir)
    r.init()
    r.add('.')
    r.commit('add', '.')
    return r.root
    
if __name__ == '__main__':
  unit_test.main()
