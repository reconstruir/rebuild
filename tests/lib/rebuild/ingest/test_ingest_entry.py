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

from rebuild.ingest.ingest_entry import ingest_entry


class test_ingest_entry(unit_test):

  def test_parse(self):
    text = '''\
entry libyaml 0.1.7

  description
    Used by python_yaml

  data
    all: checksum 0.1.7 8088e457264a98ba451a90b8661fcb4f9d6f478f7265d48322a196cec2480729
    all: checksum 0.2.2 4a9100ab61047fd9bd395bcef3ce5403365cafd55c1e0d0299cde14958e47be9

  variables
    all: _home_url=http://pyyaml.org/download/libyaml
    all: _upstream_name=yaml
    all: _upstream_filename=${_upstream_name}-${VERSION}.tar.gz
    all: _filename=${NAME}-${VERSION}.tar.gz
    all: _ingested_filename=lib/${_filename}
    
  download
    url
      all: url=${_url} ingested_filename=${_ingested_filename} checksum=@{DATA:checksum:${VERSION}}
      macos: url=${_url}.foo ingested_filename=${_ingested_filename} checksum=@{DATA:checksum:${VERSION}}
'''

    tree = tree_text_parser.parse(text, strip_comments = True)

    vm = variable_manager()
    
    r = ingest_entry.parse('<unittest>', vm, tree)

if __name__ == '__main__':
  unit_test.main()
