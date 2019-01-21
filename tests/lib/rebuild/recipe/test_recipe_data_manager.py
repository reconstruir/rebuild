#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe.recipe_data_manager import recipe_data_manager as DM
from rebuild.recipe.recipe_data_descriptor import recipe_data_descriptor as DD

class test_recipe_data_manager(unit_test):

  def test_get_empty(self):
    dm = DM()
    with self.assertRaises(KeyError) as ctx:
      dm.get('@{DATA:foo:1.2.3}')
    
  def test_set_get(self):
    dm = DM()
    dm.set('@{DATA:foo:1.2.3}', 'hi')
    self.assertEqual( 'hi', dm.get('@{DATA:foo:1.2.3}') )
    dm.set('@{DATA:foo:1.2.3}', 'bye')
    self.assertEqual( 'bye', dm.get('@{DATA:foo:1.2.3}') )
    
  def test_resolve_data_descriptor(self):
    self.assertEqual( DD('foo', '1.2.3'), DM.resolve_data_descriptor('@{DATA:foo:1.2.3}') )
    self.assertEqual( DD('foo', '1.2.3'), DM.resolve_data_descriptor( ( 'foo', '1.2.3', 'hi' ) ) )
    self.assertEqual( DD('foo', '1.2.3'), DM.resolve_data_descriptor( ( 'foo', '1.2.3' ) ) )
    self.assertEqual( DD('foo', '1.2.3'), DM.resolve_data_descriptor(DD('foo', '1.2.3')) )

  def test_set_from_tuple(self):
    dm = DM()
    dm.set_from_tuple( ( 'foo', '1.2.3', 'hi' ) )
    self.assertEqual( 'hi', dm.get('@{DATA:foo:1.2.3}') )
    dm.set_from_tuple( ( 'foo', '1.2.3', 'bye' ) )
    self.assertEqual( 'bye', dm.get('@{DATA:foo:1.2.3}') )
    
  def test_set_from_tuples(self):
    dm = DM()
    dm.set_from_tuples( [ ( 'foo', '1.2.3', 'hi' ), ( 'bar', '2.3.4', 'red' ) ] )
    self.assertEqual( 'hi', dm.get('@{DATA:foo:1.2.3}') )
    self.assertEqual( 'red', dm.get('@{DATA:bar:2.3.4}') )
    dm.set_from_tuples( [ ( 'foo', '1.2.3', 'bye' ), ( 'bar', '2.3.4', 'green' ) ] )
    self.assertEqual( 'bye', dm.get('@{DATA:foo:1.2.3}') )
    self.assertEqual( 'green', dm.get('@{DATA:bar:2.3.4}') )

  def test_substitute(self):
    dm = DM()
    dm.set_from_tuples( [ ( 'foo', '1.2.3', 'kiwi' ), ( 'bar', '2.3.4', 'red' ) ] )
    self.assertEqual( 'this is kiwi and red', dm.substitute('this is @{DATA:foo:1.2.3} and @{DATA:bar:2.3.4}') )

    with self.assertRaises(KeyError) as ctx:
      dm.substitute('this is @{DATA:baz:6.7.8}')
    
if __name__ == '__main__':
  unit_test.main()
