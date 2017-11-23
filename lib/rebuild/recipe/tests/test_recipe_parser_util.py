#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_parser_util as RPU

class test_recipe_parser_util(unit_test):

  def test_parse_key(self):
    self.assertEqual( '', RPU.parse_key('') )
    self.assertEqual( 'key', RPU.parse_key('key:True') )
    self.assertEqual( 'key', RPU.parse_key('key') )
    self.assertEqual( 'key', RPU.parse_key('key:') )
    self.assertEqual( 'f', RPU.parse_key('f:') )
    self.assertEqual( 'f', RPU.parse_key('f') )
    self.assertEqual( 'key', RPU.parse_key('key#') )
    
if __name__ == '__main__':
  unit_test.main()
