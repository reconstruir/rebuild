#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_parser, recipe_file_list, recipe_install_file_list
from bes.key_value import key_value as KV, key_value_list as KVL
from bes.text import string_list
from test_steps import *

class test_recipe_step(unit_test):

  def test_empty_defaults(self):
    text = '''\
'''
    step = self._parse(text)
    r = step.resolve_values('linux')
    expected = {
      'bool_value': False,
      'file_install_list_value': recipe_install_file_list(),
      'file_list_value': recipe_file_list(),
      'file_value': None,
      'hook_list_value': [],
      'int_value': None,
      'key_values_value': KVL(),
      'string_list_value': string_list(),
      'string_value': None,
    }
    self.assertEqual( expected, r )

    r = step.resolve_values('macos')
    self.assertEqual( expected, r )

  
  def test_takes_all(self):
    text = '''\
bool_value:
  all: True

string_list_value
  all: a b "x y"

key_values_value
  all: a=forall b=6
  linux: a=forlinux
  macos: a=formacos
  android: a=forandroid
'''
    step = self._parse(text)
    r = step.resolve_values('linux')
    expected = {
      'bool_value': True,
      'file_install_list_value': [],
      'file_list_value': [],
      'file_value': None,
      'hook_list_value': [],
      'int_value': None,
      'key_values_value': KVL([ ( 'a', 'forlinux' ), ( 'b', '6' ) ]),
      'string_list_value': ['a', 'b', '"x y"'],
      'string_value': None,
    }
    self.assertEqual( expected, r )
    r = step.resolve_values('macos')
    expected = {
      'bool_value': True,
      'file_install_list_value': [],
      'file_list_value': [],
      'file_value': None,
      'hook_list_value': [],
      'int_value': None,
      'key_values_value': KVL([ ( 'a', 'formacos' ), ( 'b', '6' ) ]),
      'string_list_value': ['a', 'b', '"x y"'],
      'string_value': None,
    }
    self.assertEqual( expected, r )
    r = step.resolve_values('android')
    expected = {
      'bool_value': True,
      'file_install_list_value': [],
      'file_list_value': [],
      'file_value': None,
      'hook_list_value': [],
      'int_value': None,
      'key_values_value': KVL([ ( 'a', 'forandroid' ), ( 'b', '6' ) ]),
      'string_list_value': ['a', 'b', '"x y"'],
      'string_value': None,
    }
    self.assertEqual( expected, r )

  @classmethod
  def _parse(clazz, s):
    recipe_template = '''!rebuild.recipe!
package foo-1.2.3-4
  steps
    step_takes_all
%s
'''
    indented_values = clazz._add_indent(s, 3)
    recipe_text = recipe_template % (indented_values)
    r = recipe_parser(recipe_text, '<test>').parse()
    return r[0].steps[0]
    
  @classmethod
  def _add_indent(clazz, s, n):
    indent = ' ' * 2 * n
    lines = s.split('\n')
    lines = [ '%s%s' % (indent, x) for x in lines ]
    return '\n'.join(lines)
    
if __name__ == '__main__':
  unit_test.main()
