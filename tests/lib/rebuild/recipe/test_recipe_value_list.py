#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_value as RV, recipe_value_list as RVL, masked_value as MV, masked_value_list as MVL
from bes.key_value import key_value_list as KVL
from bes.text import string_list
from rebuild.recipe.value import value_key_values as VKV
from rebuild.recipe.value import value_definition as VD

class test_recipe_value_list(unit_test):

  def test_resolve(self):
    values = RVL([
      RV('bool_value', [ MV('all', True) ]),
      RV('string_list_value', [ MV('all', [ 'a', 'b', '"x y"' ]) ]),
      RV('key_values_value', [
        MV('all', VKV(values = KVL([ ('a', 'forall'), ('b', '6') ]))),
        MV('linux', VKV(values = KVL([ ('a', 'forlinux') ]))),
        MV('macos', VKV(values = KVL([ ('a', 'formacos') ]))),
        MV('android', VKV(values = KVL([ ('a', 'forandroid') ]))),
        ]),
    ])

    args_definition = {
      'bool_value': VD('bool_value', 'bool', 'False', 1),
      'string_list_value': VD('string_list_value', 'string_list', '', 2),
      'key_values_value': VD('key_values_value', 'key_values', '', 3),
    }
    
    r = values.resolve('linux', args_definition)
    self.assertEqual( { 'key_values_value': KVL([ ( 'a', 'forlinux' ), ( 'b', '6' ) ]),
                        'string_list_value': ['a', 'b', '"x y"'],
                        'bool_value': True }, r )
    r = values.resolve('macos', args_definition)
    self.assertEqual( { 'key_values_value': KVL([ ( 'a', 'formacos' ), ( 'b', '6' ) ]),
                        'string_list_value': ['a', 'b', '"x y"'],
                        'bool_value': True }, r )
    r = values.resolve('android', args_definition)
    self.assertEqual( { 'key_values_value': KVL([ ( 'a', 'forandroid' ), ( 'b', '6' ) ]),
                        'string_list_value': ['a', 'b', '"x y"'],
                        'bool_value': True }, r )

  
if __name__ == '__main__':
  unit_test.main()
