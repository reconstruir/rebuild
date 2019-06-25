#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.project.ingest_file import ingest_file
from rebuild.project.ingest_file_parser import ingest_file_parser as P
from rebuild.recipe.recipe_error import recipe_error as ERR
from rebuild.base.build_target import build_target
from bes.key_value.key_value import key_value as KV
from bes.key_value.key_value_list import key_value_list as KVL
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

class test_ingest_file_parser(unit_test):

  @classmethod
  def _parse(self, text, starting_line_number = 0):
    return P(path.basename(__file__), text, starting_line_number = starting_line_number).parse()

  def test_invalid_magic(self):
    with self.assertRaises(ERR) as context:
      self._parse('nomagic')

  def test_name(self):
    text = '''!rebuild.project!
project foo
'''
    p = self._parse(text)
    self.assertEqual( 1, len(p) )
    self.assertEqual( 'foo', p[0].name )

  def test_description(self):
    text = '''!rebuild.project!
project foo
  description
    foo is nice
'''
    p = self._parse(text)
    self.assertEqual( 1, len(p) )
    self.assertEqual( 'foo', p[0].name )
    self.assertEqual( 'foo is nice', p[0].description )
    
  def test_description_multiline(self):
    text = '''!rebuild.project!
project foo
  description
    foo is nice
    very nice!
'''
    p = self._parse(text)
    self.assertEqual( 1, len(p) )
    self.assertEqual( 'foo', p[0].name )
    self.assertEqual( 'foo is nice\nvery nice!', p[0].description )

  def test_variables(self):
    text = '''!rebuild.project!
project foo
  variables
    FOO=hi BAR=666
    AUTHOR=socrates
'''
    p = self._parse(text)
    self.assertEqual( 1, len(p) )
    self.assertEqual( [ KV('FOO', 'hi'), KV('BAR', '666'), KV('AUTHOR', 'socrates') ], p[0].variables )
    
  def test_recipes(self):
    text = '''!rebuild.project!
project foo
  recipes
    for_all/foo/foo_all.recipe
    for_all/bar/bar_all.recipe

    all
      for_all2/kiwi/foo_all2.recipe
      for_all2/apple/bar_all2.recipe

    linux
      for_linux/foo/foo_linux.recipe
      for_linux/bar/bar_linux.recipe

    macos for_macos/foo/foo_macos.recipe
      for_macos/bar/bar_macos.recipe

    android for_android/foo/foo_android.recipe
            for_android/bar/bar_android.recipe
'''
    p = self._parse(text)
    self.assertEqual( 1, len(p) )
    self.assertEqual( [
      'for_all/bar/bar_all.recipe',
      'for_all/foo/foo_all.recipe',
      'for_all2/apple/bar_all2.recipe',
      'for_all2/kiwi/foo_all2.recipe',
      'for_linux/bar/bar_linux.recipe',
      'for_linux/foo/foo_linux.recipe'
    ], p[0].resolve_recipes('linux') )

    self.assertEqual( [
      'for_all/bar/bar_all.recipe',
      'for_all/foo/foo_all.recipe',
      'for_all2/apple/bar_all2.recipe',
      'for_all2/kiwi/foo_all2.recipe',
      'for_macos/bar/bar_macos.recipe',
      'for_macos/foo/foo_macos.recipe'
    ], p[0].resolve_recipes('macos') )
    
    self.assertEqual( [
      'for_all/bar/bar_all.recipe',
      'for_all/foo/foo_all.recipe',
      'for_all2/apple/bar_all2.recipe',
      'for_all2/kiwi/foo_all2.recipe',
      'for_android/bar/bar_android.recipe',
      'for_android/foo/foo_android.recipe'
    ], p[0].resolve_recipes('android') )
    
  def test_imports(self):
    text = '''!rebuild.project!
project foo
  imports
    all libraries python/packages gnu
    macos macfoo
'''
    p = self._parse(text)
    self.assertEqual( 1, len(p) )
    self.assertEqual( [
      'gnu',
      'libraries',
      'python/packages',
    ], p[0].resolve_imports('linux') )

    self.assertEqual( [
      'gnu',
      'libraries',
      'macfoo',
      'python/packages',
    ], p[0].resolve_imports('macos') )
    
  def test_python_code(self):
    text = '''!rebuild.project!
project foo
  python_code
    > print('hello from python_code inside a ingest_file')
      print('hello again')
'''
    p = self._parse(text)
    self.assertEqual( 1, len(p) )
    expected = '''\
print('hello from python_code inside a ingest_file')
print('hello again')'''
    self.assertMultiLineEqual( expected, p[0].python_code)
    
  def _filename_for_parser(self):
    'Return a fake filename for parser.  Some values need it to find files relatively to filename.'
    return self.data_path('whatever')
  
if __name__ == '__main__':
  unit_test.main()
