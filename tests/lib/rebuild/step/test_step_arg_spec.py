#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.step import step_arg_spec as AS
from rebuild.recipe.value import value_type as VT

class test_step_arg_spec(unit_test):

  def test_parse(self):
    self.assertEqual( ( 'configure_flags', VT.STRING_LIST, None, 2 ), AS.parse('configure_flags string_list', 2) )
    self.assertEqual( ( 'configure_env', VT.KEY_VALUES, None, 3 ), AS.parse('configure_env key_values', 3) )
    self.assertEqual( ( 'configure_script', VT.STRING, None, 4 ), AS.parse('configure_script string', 4) )
    self.assertEqual( ( 'need_autoreconf', VT.BOOL, None, 5 ), AS.parse('need_autoreconf bool', 5) )
    
  def test_parse_with_defaults(self):
    self.assertEqual( ( 'configure_flags', VT.STRING_LIST, 'a b c', 2 ), AS.parse('configure_flags string_list a b c', 2) )
    self.assertEqual( ( 'configure_env', VT.KEY_VALUES, 'a=5 b=6', 3 ), AS.parse('configure_env key_values a=5 b=6', 3) )
    self.assertEqual( ( 'configure_script', VT.STRING, 'foo', 4 ), AS.parse('configure_script string foo', 4) )
    self.assertEqual( ( 'need_autoreconf', VT.BOOL, 'False', 5 ), AS.parse('need_autoreconf bool False', 5) )

  def test_parse_many(self):
    text = '''
    configure_flags   string_list
    configure_env     key_values
    configure_script  string
    need_autoreconf   bool
    '''
    expected = {
      'configure_flags': AS( 'configure_flags', VT.STRING_LIST, None, 2 ),
      'configure_env': AS( 'configure_env', VT.KEY_VALUES, None, 3 ),
      'configure_script': AS( 'configure_script', VT.STRING, None, 4 ),
      'need_autoreconf': AS( 'need_autoreconf', VT.BOOL, None, 5 ),
    }
    self.assertEqual( expected, AS.parse_many(text) )
    
  def test_parse_many_with_defaults(self):
    text = '''
    configure_flags   STRING_LIST a b c
    configure_env     KEY_VALUES  a=5 b=6
    configure_script  STRING      foo
    need_autoreconf   BOOL        False
    '''
    expected = {
      'configure_flags': AS( 'configure_flags', VT.STRING_LIST, 'a b c', 2 ),
      'configure_env': AS( 'configure_env', VT.KEY_VALUES, 'a=5 b=6', 3 ),
      'configure_script': AS( 'configure_script', VT.STRING, 'foo', 4 ),
      'need_autoreconf': AS( 'need_autoreconf', VT.BOOL, 'False', 5 ),
    }
    self.assertEqual( expected, AS.parse_many(text) )
    
if __name__ == '__main__':
  unit_test.main()
