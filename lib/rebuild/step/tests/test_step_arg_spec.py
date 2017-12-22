#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.step import step_arg_spec as AS

class test_step_arg_spec(unit_test):

  def test_parse(self):
    self.assertEqual( ( 'configure_flags', 'STRING_LIST', None, 2 ), AS.parse('configure_flags string_list', 2) )
    self.assertEqual( ( 'configure_env', 'KEY_VALUES', None, 3 ), AS.parse('configure_env key_values', 3) )
    self.assertEqual( ( 'configure_script', 'STRING', None, 4 ), AS.parse('configure_script string', 4) )
    self.assertEqual( ( 'need_autoreconf', 'BOOL', None, 5 ), AS.parse('need_autoreconf bool', 5) )
    
  def test_parse_with_defaults(self):
    self.assertEqual( ( 'configure_flags', 'STRING_LIST', 'a b c', 2 ), AS.parse('configure_flags string_list a b c', 2) )
    self.assertEqual( ( 'configure_env', 'KEY_VALUES', 'a=5 b=6', 3 ), AS.parse('configure_env key_values a=5 b=6', 3) )
    self.assertEqual( ( 'configure_script', 'STRING', 'foo', 4 ), AS.parse('configure_script string foo', 4) )
    self.assertEqual( ( 'need_autoreconf', 'BOOL', 'False', 5 ), AS.parse('need_autoreconf bool False', 5) )
    
if __name__ == '__main__':
  unit_test.main()
