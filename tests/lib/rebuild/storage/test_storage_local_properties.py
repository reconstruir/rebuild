#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.files.bf_xattr_names import bf_xattr_names
from bes.testing.unit_test import unit_test

from rebuild.storage.storage_local_properties import storage_local_properties

class test_storage_local_properties(unit_test):

  def test_set_and_get(self):
    root = self.make_temp_dir()
    props = storage_local_properties(root)
    self.assertEqual( {}, props.get_properties('a/alpha-1.2.3.tar.gz') )
    props.set_properties('a/alpha-1.2.3.tar.gz', { 'rebuild.name': 'alpha', 'rebuild.version': '1.2.3' })
    props.set_properties('a/beta-1.0.tar.gz', { 'rebuild.name': 'beta' })
    self.assertEqual( { 'rebuild.name': 'alpha', 'rebuild.version': '1.2.3' }, props.get_properties('a/alpha-1.2.3.tar.gz') )
    # kept in the database, so a new instance sees them
    self.assertEqual( { 'rebuild.name': 'beta' }, storage_local_properties(root).get_properties('a/beta-1.0.tar.gz') )
    self.assertEqual( path.join(root, '.rebuild_properties.db'), props.db_filename )

  def test_replace_and_remove(self):
    props = storage_local_properties(self.make_temp_dir())
    props.set_properties('kiwi.tar.gz', { 'a': '1', 'b': '2' })
    props.set_properties('kiwi.tar.gz', { 'a': '3', 'b': None })
    self.assertEqual( { 'a': '3' }, props.get_properties('kiwi.tar.gz') )

  def test_no_xattr_is_written(self):
    root = self.make_temp_dir()
    filename = path.join(root, 'kiwi.tar.gz')
    with open(filename, 'wb') as fout:
      fout.write(b'kiwi')
    storage_local_properties(root).set_properties('kiwi.tar.gz', { 'a': '1' })
    self.assertEqual( [], bf_xattr_names.names(filename) )

  def test_a_bad_value_writes_nothing(self):
    props = storage_local_properties(self.make_temp_dir())
    with self.assertRaises(TypeError):
      props.set_properties('kiwi.tar.gz', { 'a': '1', 'b': 2 })
    self.assertEqual( {}, props.get_properties('kiwi.tar.gz') )

if __name__ == '__main__':
  unit_test.main()
