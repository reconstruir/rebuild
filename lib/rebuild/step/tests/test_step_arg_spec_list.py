#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.step import step_arg_spec_list as ASL
from rebuild.step import step_arg_spec as AS

class test_step_arg_spec_list(unit_test):

  def test_parse(self):
    text = '''
    configure_flags   string_list
    configure_env     key_values
    configure_script  string
    need_autoreconf   bool
    '''
    expected = [
      AS( 'configure_flags', 'STRING_LIST', None, 2 ),
      AS( 'configure_env', 'KEY_VALUES', None, 3 ),
      AS( 'configure_script', 'STRING', None, 4 ),
      AS( 'need_autoreconf', 'BOOL', None, 5 ),
    ]
    self.assertEqual( expected, ASL.parse(text) )
    
  def test_parse_with_defaults(self):
    text = '''
    configure_flags   STRING_LIST a b c
    configure_env     KEY_VALUES  a=5 b=6
    configure_script  STRING      foo
    need_autoreconf   BOOL        False
    '''
    expected = [
      AS( 'configure_flags', 'STRING_LIST', 'a b c', 2 ),
      AS( 'configure_env', 'KEY_VALUES', 'a=5 b=6', 3 ),
      AS( 'configure_script', 'STRING', 'foo', 4 ),
      AS( 'need_autoreconf', 'BOOL', 'False', 5 ),
    ]
    self.assertEqual( expected, ASL.parse(text) )
    
if __name__ == '__main__':
  unit_test.main()
