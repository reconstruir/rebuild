#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test

from bes.key_value.key_value_list import key_value_list

from rebuild.recipe.value.masked_value import masked_value
from rebuild.recipe.value.masked_value_list import masked_value_list
from rebuild.recipe.value.value_key_values import value_key_values
from rebuild.ingest.ingest_entry import ingest_entry as IE
from rebuild.ingest.ingest_method import ingest_method
from rebuild.ingest.ingest_unit_test import ingest_unit_test

class test_ingest_entry(unit_test):

  def test___str__(self):
    data = None
    method = ingest_unit_test.make_ingest_method('download',
                                                 'http://www.examples.com/foo.zip',
                                                 'chk',
                                                 'foo.zip')
    variables = masked_value_list([
      masked_value('all', value_key_values(value = key_value_list.parse('FOO=hello'))),
      masked_value('all', value_key_values(value = key_value_list.parse('BAR=666'))),
    ])
    
    entry = IE('foo', '1.2.3', 'foo is nice', data, variables, method)
    
    expected = '''\
entry foo 1.2.3

  description
    foo is nice

  variables
    all: FOO=hello
    all: BAR=666

  method download
    all: url=http://www.examples.com/foo.zip
    all: checksum=chk
    all: ingested_filename=foo.zip
'''

    self.assertMultiLineEqual( expected, str(entry) )


    method = None

    method_values = masked_value_list([
      masked_value('all', value_key_values(value = key_value_list.parse('url=http://www.examples.com/foo.zip'))),
      masked_value('all', value_key_values(value = key_value_list.parse('checksum=chk'))),
      masked_value('all', value_key_values(value = key_value_list.parse('ingested_filename=foo.zip'))),
    ])

    method = ingest_method('download', method_values)
    
if __name__ == '__main__':
  unit_test.main()
