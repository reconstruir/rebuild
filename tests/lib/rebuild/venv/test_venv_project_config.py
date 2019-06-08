#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.venv.venv_project_config import venv_project_config as VC
from rebuild.recipe.value.masked_value import masked_value
from rebuild.recipe.value.masked_value_list import masked_value_list
from rebuild.recipe.value.value_key_values import value_key_values
from rebuild.recipe.value.value_origin import value_origin
from rebuild.recipe.value.value_string_list import value_string_list
from bes.key_value.key_value_list import key_value_list
from bes.text.string_list import string_list
from bes.fs.temp_file import temp_file
from rebuild.base import requirement_list

class test_venv_project_config(unit_test):

  def test_str_name(self):
    p = VC(2, '<unit_test>', 'foo', None, None, None, None)
    expected = '''!rebuild.revenv!
foo
'''
    self.assertMultiLineEqual( expected, str(p) )
  
  def test_str_description(self):
    p = VC(2, '<unit_test>', 'foo', 'foo is nice\nvery very nice.', None, None, None)
    expected = '''!rebuild.revenv!
foo
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
    p = VC(2, '<unit_test>', 'foo', None, variables, None, None)
    expected = '''!rebuild.revenv!
foo
  variables
    FOO=1 BAR=hello
    BAZ=kiwi
    linux: FAST=yes AUTHOR=linus
    macos: SLOW=yes AUTHOR=genius
'''
    self.assertMultiLineEqual( expected, str(p) )
  
  def test_str_packages(self):
    packages = requirement_list.parse('forall1 == 1.1.1 forall2(all) >= 1.2 forlinux1(linux) >= 2.2 formacos1(macos) >= 3.3 forall3 >= 5.5')

    p = VC(2, '<unit_test>', 'foo', None, None, packages, None)
    expected = '''!rebuild.revenv!
foo
  packages
    all: forall1 == 1.1.1
    all: forall2 >= 1.2
    linux: forlinux1 >= 2.2
    macos: formacos1 >= 3.3
    all: forall3 >= 5.5
'''
    self.assertMultiLineEqual( expected, str(p) )

  def test_str_python_code(self):
    python_code = '''\
print('hello from python_code inside a project_file')
print('hello again')'''
    p = VC(2, '<unit_test>', 'foo', None, None, None, python_code)
    expected = '''!rebuild.revenv!
foo
  python_code
    > print('hello from python_code inside a project_file')
      print('hello again')
'''
    self.assertMultiLineEqual( expected, str(p) )

    
  def test_is_venv(self):
    text = '''!rebuild.revenv!
project foo
  recipes
    foo/foo.recipe
'''
    tmp = temp_file.make_temp_file(content = text)
    self.assertTrue( VC.is_venv_config(tmp) )
    
  def test_is_venv_config_invalid(self):
    text = '''\
[foo]
description: foo is good
packages: a b c

[bar]
description: bar is good
packages: d e f
'''
    tmp = temp_file.make_temp_file(content = text)
    self.assertFalse( VC.is_venv_config(tmp) )
    
if __name__ == '__main__':
  unit_test.main()
