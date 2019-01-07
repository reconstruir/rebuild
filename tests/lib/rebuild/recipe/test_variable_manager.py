#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe.variable_manager import variable_manager as VM
from bes.key_value import key_value_list as KVL

class test_variable_manager(unit_test):

  def test_substitute(self):
    v = VM()
    v.add_variables(KVL.parse('FOO=1.2.3 BAR=abcdefg'))
    self.assertEqual( 'FOO is 1.2.3; BAR is abcdefg', v.substitute('FOO is ${FOO}; BAR is ${BAR}') )
    
if __name__ == '__main__':
  unit_test.main()
