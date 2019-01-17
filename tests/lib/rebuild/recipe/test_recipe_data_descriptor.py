#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe.recipe_data_descriptor import recipe_data_descriptor as DD

class test_recipe_data_descriptor(unit_test):

  def test_parse(self):
    self.assertEqual( DD('foo', '1.2.3'), DD.parse('@{DATA:foo:1.2.3}') )

    with self.assertRaises(ValueError) as ctx:
      DD.parse('@DATA:foo:1.2.3')

  def test_is_data_descriptor(self):
    self.assertEqual( True, DD.is_data_descriptor('@{DATA:foo:1.2.3}') )
    self.assertEqual( False, DD.is_data_descriptor('@DATA:foo:1.2.3') )
    self.assertEqual( False, DD.is_data_descriptor('@{DATA:foo:1.2.3') )
    self.assertEqual( False, DD.is_data_descriptor('@DATA:foo:1.2.3}') )
    self.assertEqual( False, DD.is_data_descriptor('${DATA:foo:1.2.3}') )
    self.assertEqual( False, DD.is_data_descriptor('@{DATA:1.2.3}') )
    self.assertEqual( False, DD.is_data_descriptor('@{DATA::1.2.3}') )
    
  def test___str__(self):
    self.assertEqual( '@{DATA:foo:1.2.3}', str(DD('foo', '1.2.3')) )

  def test_find(self):
    self.assertEqual( [ DD('foo', '1.2.3'), DD('bar', '2.3.4') ],
                      DD.find('this is @{DATA:foo:1.2.3} and @{DATA:bar:2.3.4}') )
    self.assertEqual( [ DD('foo', '1.2.3'), DD('bar', '2.3.4') ],
                      DD.find('thisis@{DATA:foo:1.2.3}and@{DATA:bar:2.3.4}') )
    
if __name__ == '__main__':
  unit_test.main()
