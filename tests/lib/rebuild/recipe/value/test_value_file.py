#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe.value import value_file, value_origin
from bes.key_value import key_value_list

import pickle

class test_value_file(unit_test):

  ORIGIN = value_origin('foo.recipe', 6, 'text')
  PROPERTIES = key_value_list.parse('foo=x bar=y')
  
  def test_pickle(self):
    v1 = value_file(origin = self.ORIGIN, value = 'filename' , properties = self.PROPERTIES)
    s = pickle.dumps(v1)
    print('S: %s' % (s))
    v2 = pickle.loads(s)
    self.assertTrue( v1, v2 )
    
if __name__ == '__main__':
  unit_test.main()
