#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test

from bes.key_value.key_value_list import key_value_list

from rebuild.recipe.value.masked_value import masked_value
from rebuild.recipe.value.masked_value_list import masked_value_list
from rebuild.recipe.value.value_key_values import value_key_values
from rebuild.ingest.ingest_entry import ingest_entry as IE

class test_ingest_entry(unit_test):

  def test___str__(self):
    data = None
    download = None
    variables = masked_value_list([
      masked_value('all', value_key_values(value = key_value_list.parse('FOO=hello'))),
      masked_value('all', value_key_values(value = key_value_list.parse('BAR=666'))),
    ])

    entry = IE('foo', '1.2.3', 'foo is nice', data, variables, download)
    
    expected = '''\
entry foo 1.2.3

  description
    foo is nice

  variables
    all: FOO=hello
    all: BAR=666
'''

    self.assertMultiLineEqual( expected, str(entry) )
    
if __name__ == '__main__':
  unit_test.main()
