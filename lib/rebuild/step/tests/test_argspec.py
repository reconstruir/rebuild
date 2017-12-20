#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.step import step_argspec

class test_argspec(unit_test):

  def test_parse(self):
    text = '''
    configure_flags   string_list
    configure_env     key_values
    configure_script  string
    need_autoreconf   bool
    '''
    r = step_argspec.parse(text)
    self.assertEqual( [
      ( 'configure_flags', 'string_list', None, 2 ),
      ( 'configure_env', 'key_values', None, 3 ),
      ( 'configure_script', 'string', None, 4 ),
      ( 'need_autoreconf', 'bool', None, 5 ),
    ], step_argspec.parse(text) )
    
if __name__ == '__main__':
  unit_test.main()
