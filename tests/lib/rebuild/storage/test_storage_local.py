#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.common import string_util
from bes.fs.testing import temp_content
from bes.fs import temp_file
from bes.archive.temp_archive import archive_extension, temp_archive
from rebuild.storage import storage_local, storage_factory
from rebuild.config import storage_config
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

class test_storage_local(unit_test):
  
  def test_local_find_tarball(self):
    tmp_dir = source_dir_maker.make([
      'file sources/a/alpha-1.2.3.tar.gz "${tarball}" 644',
      'file sources/a/alpha-1.2.4.tar.gz "${tarball}" 644',
    ])

    tmp_cache_dir = temp_file.make_temp_dir()
    
    config = storage_config.make_local_config('unit test', tmp_dir)
    download_credentials = config.get('download', 'local')
    upload_credentials = config.get('upload', 'local')
    factory_config = storage_factory.config(tmp_cache_dir, 'sources', False, download_credentials, upload_credentials)
    storage = storage_local(factory_config)
    self.assertEqual( path.join(tmp_dir, 'sources/a/alpha-1.2.3.tar.gz'),
                      storage.find_tarball('alpha-1.2.3.tar.gz') )
    
if __name__ == '__main__':
  unit_test.main()
