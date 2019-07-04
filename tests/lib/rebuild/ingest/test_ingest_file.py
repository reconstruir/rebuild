#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.ingest.ingest_file import ingest_file as IF
from rebuild.recipe.value.masked_value import masked_value
from rebuild.recipe.value.masked_value_list import masked_value_list
from rebuild.recipe.value.value_key_values import value_key_values
from rebuild.recipe.value.value_origin import value_origin
from rebuild.recipe.value.value_string_list import value_string_list
from bes.key_value.key_value_list import key_value_list
from bes.text.string_list import string_list
from bes.fs.temp_file import temp_file

class test_ingest_file(unit_test):

  def xtest_str_name(self):
#  def __new__(clazz, format_version, filename, name, description, variables, recipes, python_code):
    p = IF(1, 'foo.reingest', 'foo', None, None, None, None)
    expected = '''!rebuild.ingest!
project foo
'''
    self.assertMultiLineEqual( expected, str(p) )
  
  def xtest_str_description(self):
    p = IF(1, 'foo.reingest', 'foo', 'foo is nice\nvery very nice.', None, None, None)
    expected = '''!rebuild.ingest!
project foo
  description
    foo is nice
    very very nice.
'''
    self.assertMultiLineEqual( expected, str(p) )
  
  def xtest_str_variables(self):
    variables = key_value_list.parse('FOO=1 BAR=hello BAZ=kiwi AUTHOR=socrates')
    p = IF(1, 'foo.reingest', 'foo', None, variables, None, None)
    expected = '''!rebuild.ingest!
project foo
  variables
    FOO=1
    BAR=hello
    BAZ=kiwi
    AUTHOR=socrates
'''
    self.assertMultiLineEqual( expected, str(p) )
  
  def xtest_str_recipes(self):
    recipes = masked_value_list([
      masked_value(None, value_string_list(value = string_list.parse('for_all/foo/foo_all.recipe'))),
      masked_value(None, value_string_list(value = string_list.parse('for_all/bar/bar_all.recipe'))),
      masked_value('linux', value_string_list(value = string_list.parse('for_linux/foo/foo_linux.recipe'))),
      masked_value('linux', value_string_list(value = string_list.parse('for_linux/bar/bar_linux.recipe'))),
      masked_value('macos', value_string_list(value = string_list.parse('for_macos/foo/foo_macos.recipe'))),
      masked_value('macos', value_string_list(value = string_list.parse('for_macos/bar/bar_macos.recipe'))),
    ])
    p = IF(1, 'foo.reingest', 'foo', None, None, recipes, None)
    expected = '''!rebuild.ingest!
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
  
  def xtest_str_python_code(self):
    python_code = '''\
print('hello from python_code inside a ingest_file')
print('hello again')'''
    p = IF(1, 'foo.reingest', 'foo', None, None, None, python_code)
    expected = '''!rebuild.ingest!
project foo
  python_code
    > print('hello from python_code inside a ingest_file')
      print('hello again')
'''
    self.assertMultiLineEqual( expected, str(p) )

  def xtest_is_ingest_file(self):
    text = '''!rebuild.ingest!
project foo
  recipes
    foo/foo.recipe
'''
    tmp = temp_file.make_temp_file(content = text)
    self.assertTrue( IF.is_ingest_file(tmp) )
    
  def xtest_is_ingest_file_invalid(self):
    text = '''def rebuild_packages():
  return [
    'foo/foo.recipe',
  ]

project foo
  recipes
    foo/foo.recipe
'''
    tmp = temp_file.make_temp_file(content = text)
    self.assertFalse( IF.is_ingest_file(tmp) )
    
if __name__ == '__main__':
  unit_test.main()
