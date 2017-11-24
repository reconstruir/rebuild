#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_parser as P, recipe_parser_error as ERR, recipe_step as RS
from rebuild.step_manager import multiple_steps, step, step_argspec, step_result
from bes.key_value import key_value as KV, key_value_list as KVL
from test_steps import *

class test_recipe_parser(unit_test):

  @classmethod
  def setUpClass(clazz):
    #unit_test.raise_skip('broken')
    pass

  def test_invalid_magic(self):
    with self.assertRaises(ERR) as context:
      self._parse('nomagic')

  def xtest_simple(self):
    text = '''#!rebuildrecipe
#comment

package foo-1.2.3-4
  properties
    category=lib
    foo="f o o"
    bar="b a r"
        baz="b a z"

  # requirements are nice
  requirements
    all: cheese >= 1.2
    linux: wine >= 2.0
    grape >= 3.0

  build_requirements
    all: kiwi >= 2.4.6

  steps
    step_setup
      copy_source_to_build_dir all:True linux:False #CFLAGS="$REBUILD_REQUIREMENTS_CFLAGS ${REBUILD_COMPILE_CFLAGS}" LDFLAGS=$REBUILD_REQUIREMENTS_LDFLAGS
        all: True
        linux: False

    step_foo

      need_something: True

      foo_env
        all: CFLAGS="$REBUILD_REQUIREMENTS_CFLAGS ${REBUILD_COMPILE_CFLAGS}"
             LDFLAGS=$REBUILD_REQUIREMENTS_LDFLAGS

      foo_flags
        all: --enable-static --disable-shared
        linux: --with-pic

      patches
        all: rebuild-foo.patch

      tests
        desktop: rebuild-foo-test1.cpp
                 rebuild-foo-test2.c
'''
    r = self._parse(text)

  def test_step_value_bool(self):
    text = '''#!rebuildrecipe
package foo-1.2.3-4
  steps
    step_takes_bool
      bool_value: True
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertEqual( 'step_takes_bool', r[0].steps[0].name )
    self.assertEqual( 1, len(r[0].steps[0].values) )
    self.assertEqual( [ ( None, 'bool_value', True ) ], r[0].steps[0].values )

  def test_step_value_bool_with_mask(self):
    text = '''#!rebuildrecipe
package foo-1.2.3-4
  steps
    step_takes_bool
      bool_value:
        all: True
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertEqual( 'step_takes_bool', r[0].steps[0].name )
    self.assertEqual( 1, len(r[0].steps[0].values) )
    self.assertEqual( [ ( 'all', 'bool_value', True ) ], r[0].steps[0].values )

  def test_step_value_key_values(self):
    text = '''#!rebuildrecipe
package foo-1.2.3-4
  steps
    step_takes_key_values
      key_values_value: a=5 b=6 c="x y"
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertEqual( 'step_takes_key_values', r[0].steps[0].name )
    self.assertEqual( 1, len(r[0].steps[0].values) )
    self.assertEqual( ( None, 'key_values_value', KVL([KV('a', '5'), KV('b', '6'), KV('c', '"x y"')]) ), r[0].steps[0].values[0] )

  def test_step_value_key_values_with_mask(self):
    text = '''#!rebuildrecipe
package foo-1.2.3-4
  steps
    step_takes_key_values
      key_values_value
        all: a=5 b=6 c="x y"
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertEqual( 'step_takes_key_values', r[0].steps[0].name )
    self.assertEqual( 1, len(r[0].steps[0].values) )
    self.assertEqual( ( 'all', 'key_values_value', KVL([KV('a', '5'), KV('b', '6'), KV('c', '"x y"')]) ), r[0].steps[0].values[0] )
    
  def test_step_value_string_list(self):
    text = '''#!rebuildrecipe
package foo-1.2.3-4
  steps
    step_takes_string_list
      string_list_value: a b "x y"
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertEqual( 'step_takes_string_list', r[0].steps[0].name )
    self.assertEqual( 1, len(r[0].steps[0].values) )
    self.assertEqual( ( None, 'string_list_value', [ 'a', 'b', '"x y"' ] ), r[0].steps[0].values[0] )

  def test_step_value_string_list_with_mask(self):
    text = '''#!rebuildrecipe
package foo-1.2.3-4
  steps
    step_takes_string_list
      string_list_value
        all: a b "x y"
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertEqual( 'step_takes_string_list', r[0].steps[0].name )
    self.assertEqual( 1, len(r[0].steps[0].values) )
    self.assertEqual( ( 'all', 'string_list_value', [ 'a', 'b', '"x y"' ] ), r[0].steps[0].values[0] )

  def test_step_value_key_values_multi_line(self):
    text = '''#!rebuildrecipe
package foo-1.2.3-4
  steps
    step_takes_key_values
      key_values_value
        all: a=5 b=6 c="x y"
             d=7 e=8
             f="kiwi apple"
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertEqual( 'step_takes_key_values', r[0].steps[0].name )
    self.assertEqual( 1, len(r[0].steps[0].values) )
    self.assertEqual( ( 'all', 'key_values_value', KVL.parse('a=5 b=6 c="x y" d=7 e=8 f="kiwi apple"', KVL.KEEP_QUOTES) ), r[0].steps[0].values[0] )
    
  def test_step_value_key_values_many_masks(self):
    text = '''#!rebuildrecipe
package foo-1.2.3-4
  steps
    step_takes_key_values
      key_values_value
        all: a=5 b=6 c="x y"
             d=7 e=8
             f="kiwi apple"
        linux: a=linux
        macos: a=macos
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertEqual( 'step_takes_key_values', r[0].steps[0].name )
    print('VALUES: %s' % (r[0].steps[0].values))
    self.assertEqual( 3, len(r[0].steps[0].values) )
    self.assertEqual( ( 'all', 'key_values_value', KVL.parse('a=5 b=6 c="x y" d=7 e=8 f="kiwi apple"', KVL.KEEP_QUOTES) ), r[0].steps[0].values[0] )
    self.assertEqual( ( 'linux', 'key_values_value', KVL.parse('a=linux', KVL.KEEP_QUOTES) ), r[0].steps[0].values[1] )
    self.assertEqual( ( 'macos', 'key_values_value', KVL.parse('a=macos', KVL.KEEP_QUOTES) ), r[0].steps[0].values[2] )

  def test_takes_all(self):
    text = '''#!rebuildrecipe
package foo-1.2.3-4
  steps
    step_takes_all
      bool_value:
        all: True

      string_list_value
        all: a b "x y"

      key_values_value
        all: a=5 b=6 c="x y"
             d=7 e=8
             f="kiwi apple"
        linux: a=linux
        macos: a=macos
'''
    r = self._parse(text)
    print('R: %s' % (str(r)))
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertEqual( 'step_takes_all', r[0].steps[0].name )
    for i, value in enumerate(r[0].steps[0].values):
      print('%d: %s' % (i, value))
    #    print('VALUE 0: %s' % (str(r[0].steps[0].values[3])))
    #    self.assertEqual( 3, len(r[0].steps[0].values) )
#    self.assertEqual( ( 'all', 'key_values_value', KVL.parse('a=5 b=6 c="x y" d=7 e=8 f="kiwi apple"', KVL.KEEP_QUOTES) ), r[0].steps[0].values[0] #)
#    self.assertEqual( ( 'linux', 'key_values_value', KVL.parse('a=linux', KVL.KEEP_QUOTES) ), r[0].steps[0].values[1] )
#    self.assertEqual( ( 'macos', 'key_values_value', KVL.parse('a=macos', KVL.KEEP_QUOTES) ), r[0].steps[0].values[2] )
    
    
  def test_multiple_steps(self):
    text = '''#!rebuildrecipe
package foo-1.2.3-4
  steps
    step_multiple
      bool_value:
        all: True

      string_list_value
        all: a b "x y"

      key_values_value
        all: a=5 b=6 c="x y"
             d=7 e=8
             f="kiwi apple"
        linux: a=linux
        macos: a=macos
'''
    r = self._parse(text)
    print('R: %s' % (str(r)))
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertEqual( 'step_multiple', r[0].steps[0].name )
    print('VALUE 0: %s' % (str(r[0].steps[0].values[3])))
    #    self.assertEqual( 3, len(r[0].steps[0].values) )
#    self.assertEqual( ( 'all', 'key_values_value', KVL.parse('a=5 b=6 c="x y" d=7 e=8 f="kiwi apple"', KVL.KEEP_QUOTES) ), r[0].steps[0].values[0] #)
#    self.assertEqual( ( 'linux', 'key_values_value', KVL.parse('a=linux', KVL.KEEP_QUOTES) ), r[0].steps[0].values[1] )
#    self.assertEqual( ( 'macos', 'key_values_value', KVL.parse('a=macos', KVL.KEEP_QUOTES) ), r[0].steps[0].values[2] )
    
  @classmethod
  def _parse(self, text):
    return P(text, '<test>').parse()
  
if __name__ == '__main__':
  unit_test.main()
