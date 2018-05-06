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

  _DEBUG = True
  
  def test_repo_source_finder(self):
    tmp_source_repo = self._make_git_repo([
      'file a/alpha-1.2.3.tar.gz "${tarball}" 644',
      'file b/beta-1.2.3.tar.gz "${tarball}" 644',
    ], delete = not self._DEBUG)
    tmp_repo_dir = temp_file.make_temp_dir(delete = not self._DEBUG)
    if self._DEBUG:
      print('tmp_source_repo: %s' % (tmp_source_repo.root))
      print('       tmp_repo_dir: %s' % (tmp_repo_dir))
    finder = repo_source_finder(tmp_repo_dir, tmp_source_repo.root)
    self.assertEqual( path.join(tmp_repo_dir, 'a/alpha-1.2.3.tar.gz'),
                      finder.find_source('alpha', '1.2.3', 'linux') )
    self.assertEqual( [ 'a/alpha-1.2.3.tar.gz', 'b/beta-1.2.3.tar.gz' ],
                      finder.repo.find_all_files() )

  def test_repo_source_finder_update(self):
    tmp_source_repo = self._make_git_repo([
      'file a/alpha-1.2.3.tar.gz "${tarball}" 644',
      'file b/beta-1.2.3.tar.gz "${tarball}" 644',
    ], delete = not self._DEBUG)
    tmp_repo_dir = temp_file.make_temp_dir(delete = not self._DEBUG)
    if self._DEBUG:
      print('tmp_source_repo: %s' % (tmp_source_repo.root))
      print('       tmp_repo_dir: %s' % (tmp_repo_dir))
    f1 = repo_source_finder(tmp_repo_dir, tmp_source_repo.root)
    self.assertEqual( path.join(tmp_repo_dir, 'a/alpha-1.2.3.tar.gz'),
                      f1.find_source('alpha', '1.2.3', 'linux') )
    self.assertEqual( [ 'a/alpha-1.2.3.tar.gz', 'b/beta-1.2.3.tar.gz' ],
                      f1.repo.find_all_files() )

    # Now add one file to the source repo
    d = source_dir_maker.make(['file g/gamma-1.2.3.tar.gz "${tarball}" 644'],
                              delete = False, where = tmp_source_repo.root)
    self.assertEqual( tmp_source_repo.root, d )
    tmp_source_repo.add('g/gamma-1.2.3.tar.gz')
    tmp_source_repo.commit('add', 'g/gamma-1.2.3.tar.gz')
    self.assertEqual( path.join(tmp_repo_dir, 'g/gamma-1.2.3.tar.gz'),
                      f1.find_source('gamma', '1.2.3', 'linux') )
    self.assertEqual( [ 'a/alpha-1.2.3.tar.gz', 'b/beta-1.2.3.tar.gz', 'g/gamma-1.2.3.tar.gz' ],
                      f1.repo.find_all_files() )

  def test_repo_source_finder_update_once(self):
    tmp_source_repo = self._make_git_repo([
      'file a/alpha-1.2.3.tar.gz "${tarball}" 644',
      'file b/beta-1.2.3.tar.gz "${tarball}" 644',
    ], delete = not self._DEBUG)
    tmp_repo_dir = temp_file.make_temp_dir(delete = not self._DEBUG)
    if self._DEBUG:
      print('tmp_source_repo: %s' % (tmp_source_repo.root))
      print('       tmp_repo_dir: %s' % (tmp_repo_dir))
    f1 = repo_source_finder(tmp_repo_dir, tmp_source_repo.root, update_only_once = True)
    self.assertEqual( path.join(tmp_repo_dir, 'a/alpha-1.2.3.tar.gz'),
                      f1.find_source('alpha', '1.2.3', 'linux') )
    self.assertEqual( [ 'a/alpha-1.2.3.tar.gz', 'b/beta-1.2.3.tar.gz' ],
                      f1.repo.find_all_files() )

    # Now add one file to the source repo
    d = source_dir_maker.make(['file g/gamma-1.2.3.tar.gz "${tarball}" 644'],
                              delete = False, where = tmp_source_repo.root)
    self.assertEqual( tmp_source_repo.root, d )
    tmp_source_repo.add('g/gamma-1.2.3.tar.gz')
    tmp_source_repo.commit('add', 'g/gamma-1.2.3.tar.gz')
    self.assertEqual( None, f1.find_source('gamma', '1.2.3', 'linux') )
    self.assertEqual( [ 'a/alpha-1.2.3.tar.gz', 'b/beta-1.2.3.tar.gz' ],
                      f1.repo.find_all_files() )

  def test_repo_source_finder_update_no_network(self):
    tmp_source_repo = self._make_git_repo([
      'file a/alpha-1.2.3.tar.gz "${tarball}" 644',
      'file b/beta-1.2.3.tar.gz "${tarball}" 644',
    ], delete = not self._DEBUG)
    tmp_repo_dir = temp_file.make_temp_dir(delete = not self._DEBUG)
    if self._DEBUG:
      print('tmp_source_repo: %s' % (tmp_source_repo.root))
      print('       tmp_repo_dir: %s' % (tmp_repo_dir))
    f1 = repo_source_finder(tmp_repo_dir, tmp_source_repo.root, no_network = True)
    self.assertEqual( None, f1.find_source('alpha', '1.2.3', 'linux') )
    self.assertEqual( [], f1.repo.find_all_files() )

  def test_repo_find_tarball(self):
    tmp_source_repo = self._make_git_repo([
      'file a/alpha-1.2.3.tar.gz "${tarball}" 644',
      'file a/alpha-1.2.4.tar.gz "${tarball}" 644',
    ], delete = not self._DEBUG)
    tmp_repo_dir = temp_file.make_temp_dir(delete = not self._DEBUG)
    if self._DEBUG:
      print('tmp_source_repo: %s' % (tmp_source_repo.root))
      print('       tmp_repo_dir: %s' % (tmp_repo_dir))
    f1 = repo_source_finder(tmp_repo_dir, tmp_source_repo.root)
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
