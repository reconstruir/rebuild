#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect, os.path as path
from bes.testing.unit_test import unit_test
from rebuild.project.project_file import project_file as PF
from rebuild.recipe.value import masked_value, masked_value_list, value_origin, value_key_values, value_string_list
from bes.key_value import key_value_list
from bes.text import string_list

class test_project_file(unit_test):

  def test_str_name(self):
#  def __new__(clazz, format_version, filename, name, description, variables, imports, recipes, python_code):
    p = PF(2, 'foo.reproject', 'foo', None, None, None, None, None)
    expected = '''!rebuild.project!
project foo
'''
    self.assertMultiLineEqual( expected, str(p) )
  
  def test_str_description(self):
    p = PF(2, 'foo.reproject', 'foo', 'foo is nice\nvery very nice.', None, None, None, None)
    expected = '''!rebuild.project!
project foo
  description
    foo is nice
    very very nice.
'''
    self.assertMultiLineEqual( expected, str(p) )
  
  def test_str_variables(self):
    variables = masked_value_list([
      masked_value(None, value_key_values(value = key_value_list.parse('FOO=1 BAR=hello'))),
      masked_value(None, value_key_values(value = key_value_list.parse('BAZ=kiwi'))),
      masked_value('linux', value_key_values(value = key_value_list.parse('FAST=yes AUTHOR=linus'))),
      masked_value('macos', value_key_values(value = key_value_list.parse('SLOW=yes AUTHOR=genius'))),
    ])
    p = PF(2, 'foo.reproject', 'foo', None, variables, None, None, None)
    expected = '''!rebuild.project!
project foo
  variables
    FOO=1 BAR=hello
    BAZ=kiwi
    linux: FAST=yes AUTHOR=linus
    macos: SLOW=yes AUTHOR=genius
'''
    self.assertMultiLineEqual( expected, str(p) )
  
  def test_str_imports(self):
    imports = masked_value_list([
      masked_value(None, value_string_list(value = string_list.parse('libs'))),
      masked_value(None, value_string_list(value = string_list.parse('gnu'))),
      masked_value('linux', value_string_list(value = string_list.parse('systemd'))),
      masked_value('macos', value_string_list(value = string_list.parse('xcode'))),
    ])
    p = PF(2, 'foo.reproject', 'foo', None, None, imports, None, None)
    expected = '''!rebuild.project!
project foo
  imports
    libs
    gnu
    linux: systemd
    macos: xcode
'''
    self.assertMultiLineEqual( expected, str(p) )
  
  def test_str_recipes(self):
    recipes = masked_value_list([
      masked_value(None, value_string_list(value = string_list.parse('for_all/foo/foo_all.recipe'))),
      masked_value(None, value_string_list(value = string_list.parse('for_all/bar/bar_all.recipe'))),
      masked_value('linux', value_string_list(value = string_list.parse('for_linux/foo/foo_linux.recipe'))),
      masked_value('linux', value_string_list(value = string_list.parse('for_linux/bar/bar_linux.recipe'))),
      masked_value('macos', value_string_list(value = string_list.parse('for_macos/foo/foo_macos.recipe'))),
      masked_value('macos', value_string_list(value = string_list.parse('for_macos/bar/bar_macos.recipe'))),
    ])
    p = PF(2, 'foo.reproject', 'foo', None, None, None, recipes, None)
    expected = '''!rebuild.project!
project foo
  recipes
    for_all/foo/foo_all.recipe
    for_all/bar/bar_all.recipe
    linux: for_linux/foo/foo_linux.recipe
    linux: for_linux/bar/bar_linux.recipe
    macos: for_macos/foo/foo_macos.recipe
    macos: for_macos/bar/bar_macos.recipe
'''
    self.assertMultiLineEqual( expected, str(p) )
  
  def test_str_python_code(self):
    recipes = masked_value_list([
      masked_value(None, value_string_list(value = string_list.parse('for_all/foo/foo_all.recipe'))),
      masked_value(None, value_string_list(value = string_list.parse('for_all/bar/bar_all.recipe'))),
      masked_value('linux', value_string_list(value = string_list.parse('for_linux/foo/foo_linux.recipe'))),
      masked_value('linux', value_string_list(value = string_list.parse('for_linux/bar/bar_linux.recipe'))),
      masked_value('macos', value_string_list(value = string_list.parse('for_macos/foo/foo_macos.recipe'))),
      masked_value('macos', value_string_list(value = string_list.parse('for_macos/bar/bar_macos.recipe'))),
    ])
    p = PF(2, 'foo.reproject', 'foo', None, None, None, recipes, None)
    expected = '''!rebuild.project!
project foo
  recipes
    for_all/foo/foo_all.recipe
    for_all/bar/bar_all.recipe
    linux: for_linux/foo/foo_linux.recipe
    linux: for_linux/bar/bar_linux.recipe
    macos: for_macos/foo/foo_macos.recipe
    macos: for_macos/bar/bar_macos.recipe
'''
    self.assertMultiLineEqual( expected, str(p) )
  
if __name__ == '__main__':
  unit_test.main()
