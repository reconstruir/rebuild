#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text.tree_text_parser import tree_text_parser
from rebuild.recipe.recipe_parser import recipe_parser as RP
from rebuild.base.build_system import build_system
from rebuild.recipe.value.value_origin import value_origin as VO
from rebuild.recipe.value.value_type import value_type as VT
from rebuild.recipe.value.masked_value import masked_value as V
from rebuild.recipe.value.masked_value_list import masked_value_list as VL
from rebuild.recipe.value import value_int

class test_masked_value_list(unit_test):

  def test_append(self):
    r = VL()
    r.append(V(None, value_int(value = 666)))
    r.append(V(None, value_int(value = 667)))
    self.assertEqual( 2, len(r) )
    
  def test_resolve_int(self):
    r = VL()
    r.append(self._int('all: 666'))
    r.append(self._int('all: 667'))
    self.assertEqual( 667, r.resolve(build_system.LINUX, VT.INT) )

  def test_resolve_string_list(self):
    r = VL()
    r.append(self._string_list('all: --all'))
    r.append(self._string_list('linux: --linux'))
    r.append(self._string_list('macos: --macos'))
    r.append(self._string_list('linux: --linux'))
    self.assertEqual( [ '--all', '--linux' ], r.resolve(build_system.LINUX, VT.STRING_LIST) )

  def test_resolve_key_values(self):
    r = VL()
    r.append(self._key_values('all: a=5 b="x y"'))
    r.append(self._key_values('linux: l=6'))
    r.append(self._key_values('macos: m=7'))
    r.append(self._key_values('linux: l=7'))
    r.append(self._key_values('linux: a=55'))
    self.assertEqual( [ ( 'a', '55' ), ( 'b', '"x y"' ), ( 'l', '7' ) ], r.resolve(build_system.LINUX, VT.KEY_VALUES) )


  @classmethod
  def _int(clazz, s):
    return RP._caca_parse_mask_and_value(VO(__file__, 1, s), s, tree_text_parser.make_node(s, 1), VT.INT)
    
  @classmethod
  def _string(clazz, s):
    return RP._caca_parse_mask_and_value(VO(__file__, 1, s), s, tree_text_parser.make_node(s, 1), VT.STRING)
    
  @classmethod
  def _bool(clazz, s):
    return RP._caca_parse_mask_and_value(VO(__file__, 1, s), s, tree_text_parser.make_node(s, 1), VT.BOOL)
    
  @classmethod
  def _string_list(clazz, s):
    return RP._caca_parse_mask_and_value(VO(__file__, 1, s), s, tree_text_parser.make_node(s, 1), VT.STRING_LIST)
    
  @classmethod
  def _key_values(clazz, s):
    return RP._caca_parse_mask_and_value(VO(__file__, 1, s), s, tree_text_parser.make_node(s, 1), VT.KEY_VALUES)
    
if __name__ == '__main__':
  unit_test.main()
