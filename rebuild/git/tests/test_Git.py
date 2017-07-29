#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest
from bes.fs import file_util, temp_file
from rebuild.git import Git

class TestGit(unittest.TestCase):

  def __create_tmp_repo(self):
    tmp_repo = temp_file.make_temp_dir()
    Git.init(tmp_repo)
    return tmp_repo

  def __create_tmp_files(self, tmp_repo):
    foo = path.join(tmp_repo, 'foo.txt')
    bar = path.join(tmp_repo, 'bar.txt')
    file_util.save(foo, content = 'foo.txt\n')
    file_util.save(bar, content = 'bar.txt\n')
    return [ 'bar.txt', 'foo.txt' ]

  def test_add(self):
    tmp_repo = self.__create_tmp_repo()
    new_files = self.__create_tmp_files(tmp_repo)
    Git.add(tmp_repo, new_files)
    expected_status = [ Git.status_item(Git.ADDED, f) for f in new_files ]
    actual_status = Git.status(tmp_repo, '.')
    self.assertEqual( expected_status, actual_status )

  def test_commit(self):
    tmp_repo = self.__create_tmp_repo()
    new_files = self.__create_tmp_files(tmp_repo)
    Git.add(tmp_repo, new_files)
    Git.commit(tmp_repo, 'nomsg\n', '.')

  def test_clone(self):
    tmp_repo = self.__create_tmp_repo()
    new_files = self.__create_tmp_files(tmp_repo)
    Git.add(tmp_repo, new_files)
    Git.commit(tmp_repo, 'nomsg\n', '.')

    cloned_tmp_repo = temp_file.make_temp_dir()
    Git.clone(tmp_repo, cloned_tmp_repo)

    expected_cloned_files = [ path.join(cloned_tmp_repo, path.basename(f)) for f in new_files ]

    for f in expected_cloned_files:
      self.assertTrue( path.exists(f) )

  def test_clone_or_update(self):
    tmp_repo = self.__create_tmp_repo()
    new_files = self.__create_tmp_files(tmp_repo)
    Git.add(tmp_repo, new_files)
    Git.commit(tmp_repo, 'nomsg\n', '.')

    cloned_tmp_repo = temp_file.make_temp_dir()
    Git.clone(tmp_repo, cloned_tmp_repo)

    expected_cloned_files = [ path.join(cloned_tmp_repo, path.basename(f)) for f in new_files ]

    for f in expected_cloned_files:
      self.assertTrue( path.exists(f) )

if __name__ == "__main__":
  unittest.main()
