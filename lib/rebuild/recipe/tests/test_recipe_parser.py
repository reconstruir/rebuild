#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_parser as P, recipe_parser_error as ERR, recipe_step as RS
from rebuild.step import compound_step, step, step_argspec, step_result
from bes.key_value import key_value as KV, key_value_list as KVL
from test_steps import *

class test_recipe_parser(unit_test):

  @classmethod
  def setUpClass(clazz):
    #unit_test.raise_skip('broken')
    pass

  @classmethod
  def _parse(self, text):
    return P(text, '<test>').parse()

  def test_invalid_magic(self):
    with self.assertRaises(ERR) as context:
      self._parse('nomagic')

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
    self.assertEqual( 'step_takes_bool\n    bool_value: True', str(r[0].steps[0]) )

  def test_step_value_bool_with_mask(self):
    self.maxDiff = None
    
    text = '''#!rebuildrecipe
package foo-1.2.3-4
  steps
    step_takes_bool
      bool_value
        all: True
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 'step_takes_bool\n  bool_value\n    all: True', str(r[0].steps[0]) )

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
    self.assertEqual( 'step_takes_key_values\n    key_values_value: a=5 b=6 c="x y"', str(r[0].steps[0]) )

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
    self.assertEqual( 'step_takes_key_values\n  key_values_value\n    all: a=5 b=6 c="x y"', str(r[0].steps[0]) )
    
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
    self.assertEqual( 'step_takes_string_list\n    string_list_value: a b "x y"', str(r[0].steps[0]) )

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
    self.assertEqual( 'step_takes_string_list\n  string_list_value\n    all: a b "x y"', str(r[0].steps[0]) )

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
    self.assertEqual( 'step_takes_key_values\n  key_values_value\n    all: a=5 b=6 c="x y" d=7 e=8 f="kiwi apple"', str(r[0].steps[0]) )
    
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
    expected = '''\
step_takes_key_values
  key_values_value
    all: a=5 b=6 c="x y" d=7 e=8 f="kiwi apple"
    linux: a=linux
    macos: a=macos'''
    self.assertEqual( expected, str(r[0].steps[0]) )

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
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 1, len(r[0].steps) )
    expected = '''\
step_takes_all
  bool_value
    all: True
  string_list_value
    all: a b "x y"
  key_values_value
    all: a=5 b=6 c="x y" d=7 e=8 f="kiwi apple"
    linux: a=linux
    macos: a=macos'''
    self.assertEqual( expected, str(r[0].steps[0]) )
    
  def test_compound_step(self):
    text = '''#!rebuildrecipe
package foo-1.2.3-4
  steps
    step_compound
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
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 1, len(r[0].steps) )
    expected = '''\
step_compound
  bool_value
    all: True
  string_list_value
    all: a b "x y"
  key_values_value
    all: a=5 b=6 c="x y" d=7 e=8 f="kiwi apple"
    linux: a=linux
    macos: a=macos'''
    self.assertEqual( expected, str(r[0].steps[0]) )
    
  def test_multiple_steps(self):
    text = '''#!rebuildrecipe
package foo-1.2.3-4
  steps
    step_takes_bool
      bool_value:
        all: True

    step_takes_string_list
      string_list_value
        all: a b "x y"

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
    self.assertEqual( 3, len(r[0].steps) )
    expected = '''\
step_takes_bool
  bool_value
    all: True
step_takes_string_list
  string_list_value
    all: a b "x y"
step_takes_key_values
  key_values_value
    all: a=5 b=6 c="x y" d=7 e=8 f="kiwi apple"
    linux: a=linux
    macos: a=macos'''
    self.assertMultiLineEqual( expected, str(r[0].steps) )
    
  def test_complete(self):
    text = '''#!rebuildrecipe
#comment

package foo-1.2.3-4
  enabled=$system is MACOS

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
    step_apple
      apple_bool_value: True

    step_kiwi
      kiwi_key_values_value
        all: CFLAGS="$REBUILD_REQUIREMENTS_CFLAGS ${REBUILD_COMPILE_CFLAGS}"
             LDFLAGS=$REBUILD_REQUIREMENTS_LDFLAGS

      kiwi_string_list_value
        all: --enable-static --disable-shared
        linux: --with-pic

    step_pear
      pear_key_values_value
        all: a=5 b=6 c="x y"

      pear_string_list_value
        all: --foo --bar --baz="x y z"
'''
    r = self._parse(text)
    expected='''\
package foo-1.2.3-4
  enabled=$system is MACOS

  properties
    bar="b a r"
    baz="b a z"
    category=lib
    foo="f o o"

  requirements
    all: cheese >= 1.2
    linux: wine >= 2.0
    all: grape >= 3.0

  build_requirements
    all: kiwi >= 2.4.6

  steps
    step_apple
      apple_bool_value: True

    step_kiwi
      kiwi_key_values_value
        all: CFLAGS="$REBUILD_REQUIREMENTS_CFLAGS ${REBUILD_COMPILE_CFLAGS}" LDFLAGS=$REBUILD_REQUIREMENTS_LDFLAGS
      kiwi_string_list_value
        all: --enable-static --disable-shared
        linux: --with-pic

    step_pear
      pear_key_values_value
        all: a=5 b=6 c="x y"
      pear_string_list_value
        all: --foo --bar --baz="x y z"'''
    self.assert_string_equal_ws( expected, str(r[0]) )
    
if __name__ == '__main__':
  unit_test.main()
