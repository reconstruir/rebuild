#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.common.string_util import string_util
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
from bes.key_value.key_value import key_value as KV
from bes.key_value.key_value_list import key_value_list as KVL

from rebuild.ingest.ingest_entry_parser import ingest_entry_parser as IEP

from rebuild.recipe.recipe_error import recipe_error
from rebuild.recipe.value.masked_value import masked_value
from rebuild.recipe.value.masked_value_list import masked_value_list
from rebuild.recipe.value.value_key_values import value_key_values

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

  data
    all: checksum 1.2.3 0123456789012345678901234567890123456789012345678901234567890123
    all: checksum 1.2.4 abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd

  variables
    all: FOO=hello
    all: BAR=666
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

    entry = self._parse(text)
    self.assertEqual( 'libfoo', entry.name )
    self.assertEqual( '1.2.3', entry.version )
    self.assertEqual( 'foo is nice', entry.description )
    self.assertEqual( masked_value_list([
      self._parse_variables('all', 'FOO=hello'),
      self._parse_variables('all', 'BAR=666'),
      self._parse_variables('all', '_home_url=http://example.com/download'),
      self._parse_variables('all', '_upstream_name=foo'),
      self._parse_variables('all', '_upstream_filename=${_upstream_name}-${VERSION}.tar.gz'),
      self._parse_variables('all', '_filename=${NAME}-${VERSION}.tar.gz'),
      self._parse_variables('all', '_ingested_filename=lib/${_filename}'),
    ]), entry.variables )
    self.assertEqual( masked_value_list([
      self._parse_data('all', 'checksum 1.2.3 0123456789012345678901234567890123456789012345678901234567890123'),
      self._parse_data('all', 'checksum 1.2.4 abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd'),
    ]), entry.data )

  def test_parse_method_download_missing_fields(self):
    text = '''\
entry libfoo 1.2.3

  method download
    all: url=http://www.examples.com/foo.zip
'''

    with self.assertRaises(recipe_error) as ctx:
      self._parse(text)

  def test_parse_method_git_missing_fields(self):
    text = '''\
entry libfoo 1.2.3

  method git
    all: address=http://www.examples.com/foo.git
'''

    with self.assertRaises(recipe_error) as ctx:
      self._parse(text)

  def xtest_resolve_method_values(self):
    text = '''\
entry libfoo 1.2.3

  method download
    linux: url=http://www.example.com/linux/foo.zip
    macos: url=http://www.example.com/macos/foo.zip
    all: checksum=foo #@{DATA:checksum:${VERSION}}
    all: ingested_filename=foo.zip #${_ingested_filename}
'''

    entry = self._parse(text)
#    self.assertEqual( [
#      ( 'url', 'http://www.example.com/macos/foo.zip' ),
#      ( 'checksum', 'foo'),
#      ( 'ingested_filename', 'foo.zip' ),
#    ], entry.resolve_method_values('macos' ) )
    self.assertEqual( [
      ( 'url', 'http://www.example.com/linux/foo.zip' ),
      ( 'checksum', 'foo'),
      ( 'ingested_filename', 'foo.zip' ),
    ], entry.resolve_method_values('linux' ) )
    
  def test_resolve_variable(self):
    text = '''\
entry libfoo 1.2.3

  variables
    all: FOO=hello
    all: BAR=default
    macos: BAR=macos
    linux: BAR=linux

  method download
    all: url=http://www.example.com/linux/foo.zip
    all: checksum=foo
    all: ingested_filename=foo.zip
'''

    entry = self._parse(text)
    self.assertEqual( [
      ( 'FOO', 'hello' ),
      ( 'BAR', 'linux'),
    ], entry.resolve_variables('linux' ) )
    self.assertEqual( [
      ( 'FOO', 'hello' ),
      ( 'BAR', 'macos'),
    ], entry.resolve_variables('macos' ) )
    self.assertEqual( [
      ( 'FOO', 'hello' ),
      ( 'BAR', 'default' ),
    ], entry.resolve_variables('android' ) )
    
  def _parse(self, text):
    tree = tree_text_parser.parse(text, strip_comments = True)
    entry_node = tree.children[0]
    vm = variable_manager()
    return IEP('<unittest>', vm).parse(entry_node, self._error)
    
  @classmethod
  def _parse_variables(clazz, mask, s):
    return masked_value(mask, value_key_values(value = key_value_list.parse(s)))
    
  @classmethod
  def _parse_data(clazz, mask, s):
    return masked_value(mask, value_string_list(value = string_list.parse(s)))
    
if __name__ == '__main__':
  unit_test.main()
