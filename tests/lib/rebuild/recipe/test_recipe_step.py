#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base import build_target
from rebuild.recipe import recipe_parser, recipe_load_env
from rebuild.recipe.value import value_file, value_file_list, value_git_address, value_install_file
from bes.key_value import key_value as KV, key_value_list as KVL
from bes.text import string_list
from test_steps import *

class test_recipe_step(unit_test):

  TEST_ENV = recipe_load_env(build_target(), None)
  
  def test_empty_defaults(self):
    text = '''\
'''
    step = self._parse(text)
    r = step.resolve_values({}, recipe_load_env(build_target(system = 'linux'), None))
    expected = {
      'bool_value': False,
      'install_file_value': [],
      'file_list_value': value_file_list(),
      'file_value': None,
      'hook_list_value': [],
      'int_value': None,
      'key_values_value': KVL(),
      'string_list_value': string_list(),
      'string_value': None,
      'git_address_value': None,
    }
    self.assertEqual( expected, r )

    r = step.resolve_values({}, recipe_load_env(build_target(system = 'macos'), None))
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
    r = step.resolve_values({}, recipe_load_env(build_target(system = 'linux'), None))
    expected = {
      'bool_value': True,
      'install_file_value': [],
      'file_list_value': [],
      'file_value': None,
      'hook_list_value': [],
      'int_value': None,
      'key_values_value': KVL([ ( 'a', 'forlinux' ), ( 'b', '6' ) ]),
      'string_list_value': ['a', 'b', '"x y"'],
      'string_value': None,
      'git_address_value': None,
    }
    self.assertEqual( expected, r )
    r = step.resolve_values({}, recipe_load_env(build_target(system = 'macos'), None))
    expected = {
      'bool_value': True,
      'install_file_value': [],
      'file_list_value': [],
      'file_value': None,
      'hook_list_value': [],
      'int_value': None,
      'key_values_value': KVL([ ( 'a', 'formacos' ), ( 'b', '6' ) ]),
      'string_list_value': ['a', 'b', '"x y"'],
      'string_value': None,
      'git_address_value': None,
    }
    self.assertEqual( expected, r )
    r = step.resolve_values({}, recipe_load_env(build_target(system = 'android'), None))
    expected = {
      'bool_value': True,
      'install_file_value': [],
      'file_list_value': [],
      'file_value': None,
      'hook_list_value': [],
      'int_value': None,
      'key_values_value': KVL([ ( 'a', 'forandroid' ), ( 'b', '6' ) ]),
      'string_list_value': ['a', 'b', '"x y"'],
      'string_value': None,
      'git_address_value': None,
    }
    self.assertEqual( expected, r )

  def test_takes_git_address(self):
    self.maxDiff = None
    text = '''\
git_address_value
  linux: linux_address linux_tag
  macos: macos_address macos_tag
'''
    step = self._parse(text)
    env = recipe_load_env(build_target(system = 'linux'), None)
    r = step.resolve_values({}, env)
    expected = {
      'bool_value': False,
      'install_file_value': [],
      'file_list_value': [],
      'file_value': None,
      'hook_list_value': [],
      'int_value': None,
      'key_values_value': [],
      'string_list_value': [],
      'string_value': None,
      'git_address_value': value_git_address(env, 'linux_address', 'linux_tag'),
    }
    self.assertEqual( expected, r )

    env = recipe_load_env(build_target(system = 'macos'), None)
    r = step.resolve_values({}, env)
    expected = {
      'bool_value': False,
      'install_file_value': [],
      'file_list_value': [],
      'file_value': None,
      'hook_list_value': [],
      'int_value': None,
      'key_values_value': [],
      'string_list_value': [],
      'string_value': None,
      'git_address_value': value_git_address(env, 'macos_address', 'macos_tag'),
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
    r = recipe_parser(clazz.TEST_ENV, '<test>', recipe_text).parse()
    return r[0].steps[0]
    
  @classmethod
  def _add_indent(clazz, s, n):
    indent = ' ' * 2 * n
    lines = s.split('\n')
    lines = [ '%s%s' % (indent, x) for x in lines ]
    return '\n'.join(lines)
    
if __name__ == '__main__':
  unit_test.main()
