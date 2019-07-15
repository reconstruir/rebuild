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
from rebuild.recipe.variable_manager import variable_manager

from bes.key_value.key_value_list import key_value_list
from bes.text.string_list import string_list
from bes.fs.temp_file import temp_file
from bes.text.tree_text_parser import tree_text_parser

from rebuild.ingest.ingest_entry_parser import ingest_entry_parser as IEP

from rebuild.recipe.recipe_error import recipe_error

class test_ingest_entry_parse(unit_test):

  @classmethod
  def _error(clazz, msg, pkg_node = None):
    if pkg_node:
      line_number = pkg_node.data.line_number
    else:
      line_number = None
    raise recipe_error(msg, '<unittest>', line_number)
  
  def test_parse(self):
    text = '''\
entry libfoo 1.2.3

  description
    foo is nice

  variables
    all: FOO=hello
    all: BAR=666

  data
    all: checksum 1.2.3 0123456789012345678901234567890123456789012345678901234567890123
    all: checksum 1.2.4 abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd

  variables
    all: _home_url=http://example.com/download
    all: _upstream_name=foo
    all: _upstream_filename=${_upstream_name}-${VERSION}.tar.gz
    all: _filename=${NAME}-${VERSION}.tar.gz
    all: _ingested_filename=lib/${_filename}

  method download
    all: url=${_url}
    all: checksum=@{DATA:checksum:${VERSION}}
    all: ingested_filename=${_ingested_filename}
'''

    tree = tree_text_parser.parse(text, strip_comments = True)
    entry_node = tree.children[0]
    vm = variable_manager()
    r = IEP('<unittest>', vm).parse(entry_node, self._error)
    print(r)
    
if __name__ == '__main__':
  unit_test.main()
