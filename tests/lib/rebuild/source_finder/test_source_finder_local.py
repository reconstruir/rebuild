#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.common import string_util
from bes.fs.testing import temp_content
from bes.fs import temp_file
from bes.archive.temp_archive import archive_extension, temp_archive
from rebuild.source_finder import source_finder_local
import os.path as path

class source_dir_maker(object):

  @classmethod
  def make(clazz, items, delete = True, where = None):
    if where:
      assert not delete
    items = [ clazz._munge_item(item) for item in items ]
    if not where:
      return temp_content.write_items_to_temp_dir(items, delete = delete)
    else:
      temp_content.write_items(items, where)
      return where

  @classmethod
  def _munge_item(clazz, item):
    ext = clazz._item_ext(item)
    assert ext
    tarball = clazz._tarball_for_ext(ext)
    return item.replace('${tarball}', tarball)
    
  @classmethod
  def _item_ext(clazz, item):
    filename = string_util.split_by_white_space(item, strip = True)[1]
    return archive_extension.extension_for_filename(filename)

  _TARBALLS = {}
  @classmethod
  def _tarball_for_ext(clazz, ext):
    if not ext in clazz._TARBALLS:
      clazz._TARBALLS[ext] = clazz.make_tarball(ext)
    return clazz._TARBALLS[ext]
  
  # Any tarball will do for the tests as long as the file type is an archive
  @classmethod
  def make_tarball(clazz, ext):
    return temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], ext).filename

class test_source_finder_local(unit_test):

  def test_local_finder_tar_gz(self):
    tmp_dir = source_dir_maker.make([
      'file a/alpha-1.2.3.tar.gz "${tarball}" 644',
      'file b/beta-1.2.3.tar.gz "${tarball}" 644',
    ])
    finder = source_finder_local(tmp_dir)
    self.assertEqual( path.join(tmp_dir, 'a/alpha-1.2.3.tar.gz'),
                      finder.find_source('alpha', '1.2.3', 'linux') )
    
  def test_local_finder_tgz(self):
    tmp_dir = source_dir_maker.make([
      'file a/alpha-1.2.3.tgz "${tarball}" 644',
      'file b/beta-1.2.3.tgz "${tarball}" 644',
    ])
    finder = source_finder_local(tmp_dir)
    self.assertEqual( path.join(tmp_dir, 'a/alpha-1.2.3.tgz'),
                      finder.find_source('alpha', '1.2.3', 'linux') )

  def test_local_finder_bz2(self):
    tmp_dir = source_dir_maker.make([
      'file a/alpha-1.2.3.bz2 "${tarball}" 644',
      'file b/beta-1.2.3.bz2 "${tarball}" 644',
    ])
    finder = source_finder_local(tmp_dir)
    self.assertEqual( path.join(tmp_dir, 'a/alpha-1.2.3.bz2'),
                      finder.find_source('alpha', '1.2.3', 'linux') )
    
  def test_local_finder_zip(self):
    tmp_dir = source_dir_maker.make([
      'file a/alpha-1.2.3.zip "${tarball}" 644',
      'file b/beta-1.2.3.zip "${tarball}" 644',
    ])
    finder = source_finder_local(tmp_dir)
    self.assertEqual( path.join(tmp_dir, 'a/alpha-1.2.3.zip'),
                      finder.find_source('alpha', '1.2.3', 'linux') )
    
  def test_local_finder_multiple_versions(self):
    tmp_dir = source_dir_maker.make([
      'file a/alpha-1.2.3.tar.gz "${tarball}" 644',
      'file a/alpha-1.2.4.tar.gz "${tarball}" 644',
      'file a/alpha-1.2.5.tar.gz "${tarball}" 644',
    ])
    finder = source_finder_local(tmp_dir)
    self.assertEqual( path.join(tmp_dir, 'a/alpha-1.2.3.tar.gz'),
                      finder.find_source('alpha', '1.2.3', 'linux') )

  def xtest_local_finder_multiple_close_versions(self):
    tmp_dir = source_dir_maker.make([
      'file a/alpha-1.2.3.tar.gz "${tarball}" 644',
      'file a/alpha-1.2.3.1.tar.gz "${tarball}" 644',
    ])
    finder = source_finder_local(tmp_dir)
    self.assertEqual( path.join(tmp_dir, 'a/alpha-1.2.3.tar.gz'),
                      finder.find_source('alpha', '1.2.3', 'linux') )
    
  def test_local_finder_invalid_archive(self):
    tmp_dir = source_dir_maker.make([
      'file a/alpha-1.2.3.tar.gz "alpha-1.2.3.tar.gz" 644',
      'file b/beta-1.2.3.tar.gz "beta-1.2.3.tar.gz" 644',
    ])
    finder = source_finder_local(tmp_dir)
    with self.assertRaises(RuntimeError) as context:
      finder.find_source('alpha', '1.2.3', 'linux')
    
  def test_local_finder_platform_specific(self):
    tmp_dir = source_dir_maker.make([
      'file a/linux/alpha-linux-1.2.3.tar.gz "${tarball}" 644',
      'file a/macos/alpha-macos-1.2.3.tar.gz "${tarball}" 644',
    ])
    finder = source_finder_local(tmp_dir)
    self.assertEqual( path.join(tmp_dir, 'a/linux/alpha-linux-1.2.3.tar.gz'),
                      finder.find_source('alpha', '1.2.3', 'linux') )
    self.assertEqual( path.join(tmp_dir, 'a/macos/alpha-macos-1.2.3.tar.gz'),
                      finder.find_source('alpha', '1.2.3', 'macos') )
    
  def test_local_finder_darwin_alias_for_macos_subdir(self):
    tmp_dir = source_dir_maker.make([
      'file a/linux/alpha-linux-1.2.3.tar.gz "${tarball}" 644',
      'file a/darwin/alpha-darwin-1.2.3.tar.gz "${tarball}" 644',
    ])
    finder = source_finder_local(tmp_dir)
    self.assertEqual( path.join(tmp_dir, 'a/linux/alpha-linux-1.2.3.tar.gz'),
                      finder.find_source('alpha', '1.2.3', 'linux') )
    self.assertEqual( path.join(tmp_dir, 'a/darwin/alpha-darwin-1.2.3.tar.gz'),
                      finder.find_source('alpha', '1.2.3', 'macos') )

  def test_local_finder_darwin_alias_for_macos_mixed_case(self):
    tmp_dir = source_dir_maker.make([
      'file a/alpha-LINUX-1.2.3.tar.gz "${tarball}" 644',
      'file a/alpha-Darwin-1.2.3.tar.gz "${tarball}" 644',
    ])
    finder = source_finder_local(tmp_dir)
    self.assertEqual( path.join(tmp_dir, 'a/alpha-LINUX-1.2.3.tar.gz'),
                      finder.find_source('alpha', '1.2.3', 'linux') )
    self.assertEqual( path.join(tmp_dir, 'a/alpha-Darwin-1.2.3.tar.gz'),
                      finder.find_source('alpha', '1.2.3', 'macos') )
    
  def test_local_find_tarball(self):
    tmp_dir = source_dir_maker.make([
      'file a/alpha-1.2.3.tar.gz "${tarball}" 644',
      'file a/alpha-1.2.4.tar.gz "${tarball}" 644',
    ])
    finder = source_finder_local(tmp_dir)
    self.assertEqual( path.join(tmp_dir, 'a/alpha-1.2.3.tar.gz'),
                      finder.find_tarball('alpha-1.2.3.tar.gz') )
    
if __name__ == '__main__':
  unit_test.main()
