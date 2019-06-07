#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.common.string_util import string_util
from bes.fs.testing.temp_content import temp_content
from bes.fs.temp_file import temp_file
from bes.archive.archive_extension import archive_extension
from bes.archive.temp_archive import temp_archive
from rebuild.storage import storage_local, storage_factory
from rebuild.config import storage_config_manager
import os.path as path
from _rebuild_testing.artifact_manager_tester import artifact_manager_tester as AMT

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
      'file rebuild_stuff/sources/a/alpha-1.2.3.tar.gz "${tarball}" 644',
      'file rebuild_stuff/sources/a/alpha-1.2.4.tar.gz "${tarball}" 644',
    ], delete = not self.DEBUG)

    tmp_cache_dir = temp_file.make_temp_dir(suffix = '.local_cache_dir', delete = not self.DEBUG)

    if self.DEBUG:
      print('tmp_dir: %s' % (tmp_dir))
      print('tmp_cache_dir: %s' % (tmp_cache_dir))
    
    scm = storage_config_manager.make_local_config('unit_test', tmp_dir, 'rebuild_stuff', None)
    config = scm.get('unit_test')
    factory_config = storage_factory.config(tmp_cache_dir, 'sources', True, config)
    storage = storage_local(factory_config)
    expected = path.join(tmp_cache_dir, 'a/alpha-1.2.3.tar.gz')
    actual = storage.find_tarball('a/alpha-1.2.3.tar.gz')
    self.assertEqual( expected, actual )
    
  def test_list_all_files(self):
    water_recipes = '''
fake_package water 1.0.0 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.1 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.10 0 0 linux release x86_64 ubuntu 18 none
fake_package water 1.0.13 0 0 linux release x86_64 ubuntu 18 none

fake_package water 1.0.0 0 0 linux release x86_64 centos 7 none
fake_package water 1.0.1 0 0 linux release x86_64 centos 7 none
fake_package water 1.0.9 0 0 linux release x86_64 centos 7 none
fake_package water 1.0.11 0 0 linux release x86_64 centos 7 none

fake_package water 1.0.0 0 0 macos release x86_64 none 10 none
fake_package water 1.0.1 0 0 macos release x86_64 none 10 none
fake_package water 1.0.9 0 0 macos release x86_64 none 10 none
fake_package water 1.0.11 0 0 macos release x86_64 none 10 none
'''

    milk_recipes = '''
fake_package milk 1.0.0 0 0 linux release x86_64 ubuntu 18 none
fake_package milk 1.0.1 0 0 linux release x86_64 ubuntu 18 none
fake_package milk 1.0.1 1 0 linux release x86_64 ubuntu 18 none
fake_package milk 1.0.10 0 0 linux release x86_64 ubuntu 18 none
fake_package milk 1.0.13 0 0 linux release x86_64 ubuntu 18 none

fake_package milk 1.0.0 0 0 linux release x86_64 centos 7 none
fake_package milk 1.0.1 0 0 linux release x86_64 centos 7 none
fake_package milk 1.0.9 0 0 linux release x86_64 centos 7 none
fake_package milk 1.0.11 0 0 linux release x86_64 centos 7 none

fake_package milk 1.0.0 0 0 macos release x86_64 none 10 none
fake_package milk 1.0.1 0 0 macos release x86_64 none 10 none
fake_package milk 1.0.9 0 0 macos release x86_64 none 10 none
fake_package milk 1.0.11 0 0 macos release x86_64 none 10 none

'''
    t = AMT(debug = self.DEBUG)
    t.add_recipes(water_recipes)
    t.add_recipes(milk_recipes)
    t.publish(water_recipes)
    t.publish(milk_recipes)

    tmp_cache_dir = temp_file.make_temp_dir(suffix = '.local_cache_dir', delete = not self.DEBUG)
    tmp_dir = t.am.root_dir
    if self.DEBUG:
      print('tmp_dir: %s' % (tmp_dir))
      print('tmp_cache_dir: %s' % (tmp_cache_dir))
    
    scm = storage_config_manager.make_local_config('unit_test', tmp_dir, None, None)
    config = scm.get('unit_test')
    factory_config = storage_factory.config(tmp_cache_dir, None, True, config)
    storage = storage_local(factory_config)
    expected = [
      'linux-centos-7/x86_64/release/milk-1.0.0.tar.gz',
      'linux-centos-7/x86_64/release/milk-1.0.1.tar.gz',
      'linux-centos-7/x86_64/release/milk-1.0.11.tar.gz',
      'linux-centos-7/x86_64/release/milk-1.0.9.tar.gz',
      'linux-centos-7/x86_64/release/water-1.0.0.tar.gz',
      'linux-centos-7/x86_64/release/water-1.0.1.tar.gz',
      'linux-centos-7/x86_64/release/water-1.0.11.tar.gz',
      'linux-centos-7/x86_64/release/water-1.0.9.tar.gz',
      'linux-ubuntu-18/x86_64/release/milk-1.0.0.tar.gz',
      'linux-ubuntu-18/x86_64/release/milk-1.0.1-1.tar.gz',
      'linux-ubuntu-18/x86_64/release/milk-1.0.1.tar.gz',
      'linux-ubuntu-18/x86_64/release/milk-1.0.10.tar.gz',
      'linux-ubuntu-18/x86_64/release/milk-1.0.13.tar.gz',
      'linux-ubuntu-18/x86_64/release/water-1.0.0.tar.gz',
      'linux-ubuntu-18/x86_64/release/water-1.0.1.tar.gz',
      'linux-ubuntu-18/x86_64/release/water-1.0.10.tar.gz',
      'linux-ubuntu-18/x86_64/release/water-1.0.13.tar.gz',
      'macos-10/x86_64/release/milk-1.0.0.tar.gz',
      'macos-10/x86_64/release/milk-1.0.1.tar.gz',
      'macos-10/x86_64/release/milk-1.0.11.tar.gz',
      'macos-10/x86_64/release/milk-1.0.9.tar.gz',
      'macos-10/x86_64/release/water-1.0.0.tar.gz',
      'macos-10/x86_64/release/water-1.0.1.tar.gz',
      'macos-10/x86_64/release/water-1.0.11.tar.gz',
      'macos-10/x86_64/release/water-1.0.9.tar.gz',
    ]
    self.assertEqual( expected, storage.list_all_files() )
    
if __name__ == '__main__':
  unit_test.main()
