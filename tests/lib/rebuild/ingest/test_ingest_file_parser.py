#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.ingest.ingest_file import ingest_file
from rebuild.ingest.ingest_file_parser import ingest_file_parser as P
from rebuild.recipe.recipe_error import recipe_error as ERR
from rebuild.base.build_target import build_target
from bes.key_value.key_value import key_value as KV
from bes.key_value.key_value_list import key_value_list as KVL
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.testing.unit_test_skip import raise_skip

class test_ingest_file_parser(unit_test):

  @classmethod
  def _parse(self, text, starting_line_number = 0):
    return P(path.basename(__file__), text, starting_line_number = starting_line_number).parse()

  def test_invalid_magic(self):
    with self.assertRaises(ERR) as context:
      self._parse('nomagic')

  def test_description(self):
    text = '''!rebuild.ingest.v1!
description
  foo is nice
'''
    f = self._parse(text)
    self.assertEqual( 'foo is nice', f.description )
    
  def test_variables(self):
    text = '''!rebuild.ingest.v1!
variables
  FOO=hello
  BAR=666

'''
    f = self._parse(text)
    self.assertEqual( [
      ( 'FOO',  'hello' ),
      ( 'BAR',  '666' ),
    ], f.variables)
  
  def test_entries(self):
    text = '''!rebuild.ingest.v1!
entry libfoo 1.2.3

  data
    all: checksum 1.2.3 0123456789001234567890012345678900123456789001234567890012345678
    all: checksum 1.2.4 abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd

  variables
    all: _home_url=http://example.com/foo
    all: _upstream_name=foo
    all: _upstream_filename=${_upstream_name}-${VERSION}.tar.gz
    all: _filename=${NAME}-${VERSION}.tar.gz
    all: _ingested_filename=lib/${_filename}

  method download
    all: url=http://www.examples.com/foo.zip
    all: checksum=chk
    all: ingested_filename=foo.zip
'''
    f = self._parse(text)
    print(f.entries)
    
if __name__ == '__main__':
  unit_test.main()
