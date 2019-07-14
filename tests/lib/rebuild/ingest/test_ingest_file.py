#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.ingest.ingest_file import ingest_file as IF
from rebuild.recipe.value.masked_value import masked_value
from rebuild.recipe.value.masked_value_list import masked_value_list
from rebuild.recipe.value.value_key_values import value_key_values
from rebuild.recipe.value.value_origin import value_origin
from rebuild.recipe.value.value_string_list import value_string_list
from bes.key_value.key_value_list import key_value_list
from bes.text.string_list import string_list
from bes.fs.temp_file import temp_file

class test_ingest_file(unit_test):

  def test_parse(self):
    p = IF(IF.FORMAT_VERSION, 'foo.reingest', 'foo is nice', None, None)
    expected = '''\
!rebuild.ingest!

description
  foo is nice
'''
    self.assertMultiLineEqual( expected, str(p) )
  
    
if __name__ == '__main__':
  unit_test.main()
