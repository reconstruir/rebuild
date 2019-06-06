#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base import build_target
from rebuild.recipe import recipe_parser, testing_recipe_load_env
from rebuild.recipe.value import value_file, value_file_list, value_git_address, value_install_file
from rebuild.recipe.value import value_origin as VO
from rebuild.recipe.variable_manager import variable_manager
from bes.key_value.key_value import key_value as KV
from bes.key_value.key_value_list import key_value_list as KVL
from bes.text import string_list
from bes.git import git_address
from test_steps import *

class test_recipe_step(unit_test):

  BT_LINUX = build_target('linux', 'ubuntu', '18', '', ( 'x86_64' ), 'release')
  BT_MACOS = build_target('macos', '', '', '', ( 'x86_64' ), 'release')
  BT_ANDROID = build_target('android', '', '', '', ( 'armv7' ), 'release')
  
  def test_empty_defaults(self):
    text = '''\
'''
    step = self._parse(text)
    r = step.resolve_values({}, testing_recipe_load_env(self.BT_LINUX))
    expected = {
      'bool_value': False,
      'install_file_value': [],
      'file_list_value': value_file_list(),
      'file_value': None,
      'hook_value': [],
      'int_value': None,
      'key_values_value': KVL(),
      'string_list_value': string_list(),
      'string_value': None,
      'git_address_value': None,
    }
    self.assertEqual( expected, r )

    r = step.resolve_values({}, testing_recipe_load_env(self.BT_MACOS))
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
    r = step.resolve_values({}, testing_recipe_load_env(self.BT_LINUX))
    expected = {
      'bool_value': True,
      'install_file_value': [],
      'file_list_value': [],
      'file_value': None,
      'hook_value': [],
      'int_value': None,
      'key_values_value': KVL([ ( 'a', 'forlinux' ), ( 'b', '6' ) ]),
      'string_list_value': ['a', 'b', '"x y"'],
      'string_value': None,
      'git_address_value': None,
    }
    self.assertEqual( expected, r )
    r = step.resolve_values({}, testing_recipe_load_env(self.BT_MACOS))
    expected = {
      'bool_value': True,
      'install_file_value': [],
      'file_list_value': [],
      'file_value': None,
      'hook_value': [],
      'int_value': None,
      'key_values_value': KVL([ ( 'a', 'formacos' ), ( 'b', '6' ) ]),
      'string_list_value': ['a', 'b', '"x y"'],
      'string_value': None,
      'git_address_value': None,
    }
    self.assertEqual( expected, r )
    r = step.resolve_values({}, testing_recipe_load_env(self.BT_ANDROID))
    expected = {
      'bool_value': True,
      'install_file_value': [],
      'file_list_value': [],
      'file_value': None,
      'hook_value': [],
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
    env = testing_recipe_load_env(self.BT_LINUX)
    r = step.resolve_values({}, env)
    expected = {
      'bool_value': False,
      'install_file_value': [],
      'file_list_value': [],
      'file_value': None,
      'hook_value': [],
      'int_value': None,
      'key_values_value': [],
      'string_list_value': [],
      'string_value': None,
      'git_address_value': value_git_address(origin = VO('caca', 1, 'caca'),
                                             value = git_address('linux_address', 'linux_tag')),
    }
    self.assertEqual( expected, r )

    env = testing_recipe_load_env(self.BT_MACOS)
    r = step.resolve_values({}, env)
    expected = {
      'bool_value': False,
      'install_file_value': [],
      'file_list_value': [],
      'file_value': None,
      'hook_value': [],
      'int_value': None,
      'key_values_value': [],
      'string_list_value': [],
      'string_value': None,
      'git_address_value': value_git_address(origin = VO('caca', 1, 'caca'),
                                             value = git_address('macos_address', 'macos_tag')),
    }
    self.assertEqual( expected, r )
    
  @classmethod
  def _parse(clazz, s):
    recipe_template = '''!rebuild.recipe!
package foo 1.2.3 4
  steps
    step_takes_all
%s
'''
    indented_values = clazz._add_indent(s, 3)
    recipe_text = recipe_template % (indented_values)
    r = recipe_parser('<test>', recipe_text).parse(variable_manager())
    return r[0].steps[0]
    
  @classmethod
  def _add_indent(clazz, s, n):
    indent = ' ' * 2 * n
    lines = s.split('\n')
    lines = [ '%s%s' % (indent, x) for x in lines ]
    return '\n'.join(lines)
    
if __name__ == '__main__':
  unit_test.main()
