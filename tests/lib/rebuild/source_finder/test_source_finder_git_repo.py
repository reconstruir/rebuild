#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.testing import temp_content
from bes.fs import temp_file
from bes.git import repo
from rebuild.source_finder import source_finder_git_repo
import os.path as path

from test_source_finder_local import source_dir_maker

class test_source_finder_git_repo(unit_test):

  DEBUG = False
  #DEBUG = True

  def test_repo_find_tarball(self):
    tmp_source_repo = self._make_git_repo([
      'file a/alpha-1.2.3.tar.gz "${tarball}" 644',
      'file a/alpha-1.2.4.tar.gz "${tarball}" 644',
    ], delete = not self.DEBUG)
    tmp_repo_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print('tmp_source_repo: %s' % (tmp_source_repo.root))
      print('       tmp_repo_dir: %s' % (tmp_repo_dir))
    f1 = source_finder_git_repo(tmp_repo_dir, tmp_source_repo.root)
    self.assertEqual( path.join(tmp_repo_dir, 'a/alpha-1.2.3.tar.gz'), f1.find_tarball('alpha-1.2.3.tar.gz') )
    
  @classmethod
  def _make_git_repo(clazz, items, delete = True):
    tmp_source_dir = source_dir_maker.make(items, delete = True)
    r = repo(tmp_source_dir)
    r.init()
    r.add('.')
    r.commit('add', '.')
    return r
    
if __name__ == '__main__':
  unit_test.main()
