#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe.recipe_value import recipe_value as RV
from rebuild.recipe.recipe_value_list import recipe_value_list as RVL
from bes.key_value.key_value_list import key_value_list as KVL
from bes.text.string_list import string_list
from rebuild.recipe.value import value_key_values as VKV
from rebuild.recipe.value import value_definition as VD
from rebuild.recipe.value.masked_value import masked_value as MV
from rebuild.recipe.value.masked_value_list import masked_value_list as MVL
from rebuild.recipe.value import value_bool
from rebuild.recipe.value import value_string_list

class test_recipe_value_list(unit_test):

  def test_resolve(self):
    values = RVL([
      RV('bool_value', [ MV('all', value_bool(value = True)) ]),
      RV('string_list_value', [ MV('all', value_string_list(value = [ 'a', 'b', '"x y"' ])) ]),
      RV('key_values_value', [
        MV('all', VKV(value = KVL([ ('a', 'forall'), ('b', '6') ]))),
        MV('linux', VKV(value = KVL([ ('a', 'forlinux') ]))),
        MV('macos', VKV(value = KVL([ ('a', 'formacos') ]))),
        MV('android', VKV(value = KVL([ ('a', 'forandroid') ]))),
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
