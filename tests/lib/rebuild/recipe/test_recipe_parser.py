#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect, os.path as path
from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe, recipe_parser as P, recipe_parser_error as ERR, recipe_step as RS, recipe_load_env
from rebuild.step import compound_step, step, step_result
from bes.key_value import key_value as KV, key_value_list as KVL
from bes.fs import file_util, temp_file
from test_steps import *

class test_recipe_parser(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/recipe_parser'

  TEST_ENV = recipe_load_env(None, None)
  
  @classmethod
  def _parse(self, text, starting_line_number = 0):
    return P(self.TEST_ENV, path.basename(__file__), text, starting_line_number = starting_line_number).parse()

  @classmethod
  def setUpClass(clazz):
    clazz.SAVE_CHECK_UNKNOWN_PROPERTIES = recipe.CHECK_UNKNOWN_PROPERTIES
    recipe.CHECK_UNKNOWN_PROPERTIES = False

  @classmethod
  def tearDownClass(clazz):
    recipe.CHECK_UNKNOWN_PROPERTIES = clazz.SAVE_CHECK_UNKNOWN_PROPERTIES
  
  def test_invalid_magic(self):
    with self.assertRaises(ERR) as context:
      self._parse('nomagic')

  def test_package_version_dash(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )

  def test_package_version_space(self):
    frame = inspect.getframeinfo(inspect.currentframe())
    text = '''!rebuild.recipe!
package foo 1.2.3-4
'''
    r = self._parse(text, frame.lineno)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    
  def test_step_value_bool(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4
  steps
    step_takes_bool
      bool_value: True
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertMultiLineEqual( 'step_takes_bool\n    bool_value: True', str(r[0].steps[0]) )

  def test_step_value_bool_with_mask(self):
    self.maxDiff = None
    
    text = '''!rebuild.recipe!
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
    self.assertMultiLineEqual( 'step_takes_bool\n  bool_value\n    all: True', str(r[0].steps[0]) )

  def test_step_value_key_values(self):
    text = '''!rebuild.recipe!
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
    self.assertMultiLineEqual( 'step_takes_key_values\n    key_values_value: a=5 b=6 c="x y"', str(r[0].steps[0]) )

  def test_step_value_key_values_with_mask(self):
    text = '''!rebuild.recipe!
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
    self.assertMultiLineEqual( 'step_takes_key_values\n  key_values_value\n    all: a=5 b=6 c="x y"', str(r[0].steps[0]) )

  def test_step_value_string(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4
  steps
    step_takes_string
      string_value: my string with spaces
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_string\n    string_value: my string with spaces', str(r[0].steps[0]) )

  def test_step_value_string_with_quotes(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4
  steps
    step_takes_string
      string_value: my string with "a quote"
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_string\n    string_value: my string with "a quote"', str(r[0].steps[0]) )

  def test_step_value_string_with_comments(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4
  steps
    step_takes_string
      string_value: my string # comment
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_string\n    string_value: my string', str(r[0].steps[0]) )
    
  def test_step_value_string_with_hash_in_quotes(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4
  steps
    step_takes_string
      string_value: "my string # with a hash"
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_string\n    string_value: "my string # with a hash"', str(r[0].steps[0]) )
    
  def test_step_value_string_list(self):
    text = '''!rebuild.recipe!
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
    self.assertMultiLineEqual( 'step_takes_string_list\n    string_list_value: a b "x y"', str(r[0].steps[0]) )

  def test_step_value_string_list_with_mask(self):
    text = '''!rebuild.recipe!
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
    self.assertMultiLineEqual( 'step_takes_string_list\n  string_list_value\n    all: a b "x y"', str(r[0].steps[0]) )

  def test_step_value_string_list_with_comment(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4
  steps
    step_takes_string_list
      string_list_value: a b "x y" # comment
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_string_list\n    string_list_value: a b "x y"', str(r[0].steps[0]) )
    
  def test_step_value_string_list_with_quoted_hash(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4
  steps
    step_takes_string_list
      string_list_value: a b "x # y"
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_string_list\n    string_list_value: a b "x # y"', str(r[0].steps[0]) )
    
  def test_step_value_key_values_multi_line(self):
    text = '''!rebuild.recipe!
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
    self.assertMultiLineEqual( 'step_takes_key_values\n  key_values_value\n    all: a=5 b=6 c="x y" d=7 e=8 f="kiwi apple"', str(r[0].steps[0]) )
    
  def test_step_value_key_values_many_masks(self):
    text = '''!rebuild.recipe!
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
    text = '''!rebuild.recipe!
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
    text = '''!rebuild.recipe!
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
    text = '''!rebuild.recipe!
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

  def test_env_vars(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4
  steps
    step_takes_bool
      bool_value: True

  env_vars
    all: foo=5 bar=6
    linux: baz=forlinux
    macos: baz=formacos

'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertMultiLineEqual( 'step_takes_bool\n    bool_value: True', str(r[0].steps[0]) )
    
  def test_complete(self):
    self.maxDiff = None
    text = '''!rebuild.recipe!
#comment

package foo-1.2.3-4
  enabled=$system is MACOS

  properties
    foo="f o o"
    bar="b a r"
        baz="b a z"

  # requirements are nice
  requirements
    all: cheese >= 1.2
    linux: wine >= 2.0
    grape >= 3.0

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
    foo="f o o"

  requirements
    all: cheese >= 1.2
    linux: wine >= 2.0
    all: grape >= 3.0

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
    actual = r[0].to_string(indent = 2)
    self.assertMultiLineEqual( expected, actual )

  def test_step_load(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4
  load
    test_loaded_step1.py
    test_loaded_step2.py

  steps
    test_loaded_step1
      bool_value: True

    test_loaded_step2
      bool_value: True
'''

    r = P(self.TEST_ENV, self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 'test_loaded_step1\n    bool_value: True', str(r[0].steps[0]) )
    self.assertEqual( 'test_loaded_step2\n    bool_value: True', str(r[0].steps[1]) )

  def test_step_value_hook_list(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4
  load
    test_loaded_hook1.py
    test_loaded_hook2.py

  steps
    step_takes_hook_list
      hook_list_value
        all: test_loaded_hook1
        all: test_loaded_hook2
'''
    expected_hook1_filename = self.data_path('test_loaded_hook1.py')
    expected_hook2_filename = self.data_path('test_loaded_hook2.py')

    r = P(self.TEST_ENV, expected_hook1_filename, text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_hook_list\n  hook_list_value\n    all: test_loaded_hook1\n    all: test_loaded_hook2', str(r[0].steps[0]) )
    actual_hook1_filename = r[0].steps[0].values[0].values[0].value[0].filename
    actual_hook2_filename = r[0].steps[0].values[0].values[1].value[0].filename
    self.assertEqual( expected_hook1_filename, actual_hook1_filename )
    self.assertEqual( expected_hook2_filename, actual_hook2_filename )
    
  def test_step_value_hook_list_with_mask(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4
  load
    test_loaded_hook3.py
    test_loaded_hook4.py

  steps
    step_takes_hook_list
      hook_list_value
        linux: test_loaded_hook3
        linux:  test_loaded_hook4
'''
    expected_hook3_filename = self.data_path('test_loaded_hook3.py')
    expected_hook4_filename = self.data_path('test_loaded_hook4.py')
    
    r = P(self.TEST_ENV, expected_hook3_filename, text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_hook_list\n  hook_list_value\n    linux: test_loaded_hook3\n    linux: test_loaded_hook4', str(r[0].steps[0]) )
    actual_hook3_filename = r[0].steps[0].values[0].values[0].value[0].filename
    actual_hook4_filename = r[0].steps[0].values[0].values[1].value[0].filename
    self.assertEqual( expected_hook3_filename, actual_hook3_filename )
    self.assertEqual( expected_hook4_filename, actual_hook4_filename )

  def test_step_value_file_list(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4

  steps
    step_takes_file_list
      file_list_value: test_file1.txt test_file2.txt
'''
    r = P(self.TEST_ENV, self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_file_list\n    file_list_value: test_file1.txt test_file2.txt', str(r[0].steps[0]) )

  def test_step_value_file(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4

  steps
    step_takes_file
      file_value: test_file1.txt
'''
    r = P(self.TEST_ENV, self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_file\n    file_value: test_file1.txt', str(r[0].steps[0]) )

  def test_step_value_file_with_values(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4

  steps
    step_takes_file
      file_value: test_file1.txt foo=1 bar=2 baz=\"hello kiwi\"
'''
    r = P(self.TEST_ENV, self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_file\n    file_value: test_file1.txt foo=1 bar=2 baz=\"hello kiwi\"', str(r[0].steps[0]) )

  def test_step_value_install_file(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4

  steps
    step_takes_install_file
      install_file_value: test_file1.txt etc/foo/f1.txt
'''
    r = P(self.TEST_ENV, self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_install_file\n    install_file_value: test_file1.txt etc/foo/f1.txt', str(r[0].steps[0]) )

  def test_step_value_install_file_many(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4

  steps
    step_takes_install_file
      install_file_value
        all: test_file1.txt etc/foo/f1.txt
        all: test_file2.txt etc/foo/f2.txt
'''
    r = P(self.TEST_ENV, self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_install_file\n  install_file_value\n    all: test_file1.txt etc/foo/f1.txt\n    all: test_file2.txt etc/foo/f2.txt', str(r[0].steps[0]) )


  def test_step_comments(self):
    text = '''!rebuild.recipe!
# comment
package foo-1.2.3-4 # comment
# comment
  # comment
  steps # comment
    # comment
# comment
    step_takes_bool # comment
      # comment
# comment
      bool_value: True # comment
      # comment
# comment
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertMultiLineEqual( 'step_takes_bool\n    bool_value: True', str(r[0].steps[0]) )

  def test_step_empty_value(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4
  steps
    step_takes_bool
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertMultiLineEqual( 'step_takes_bool', str(r[0].steps[0]) )

  def test_step_value_file_list(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4

  steps
    step_takes_file_list
      file_list_value: test_file1.txt test_file2.txt
'''
    r = P(self.TEST_ENV, self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_file_list\n    file_list_value: test_file1.txt test_file2.txt', str(r[0].steps[0]) )

  def test_step_git_address(self):
    text = '''!rebuild.recipe!
package foo-1.2.3-4

  steps
    step_takes_git_address
      git_address_value: test_file1.txt test_file2.txt
'''
    r = P(self.TEST_ENV, self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_git_address\n    git_address_value: test_file1.txt test_file2.txt', str(r[0].steps[0]) )
    
  def _filename_for_parser(self):
    'Return a fake filename for parser.  Some values need it to find files relatively to filename.'
    return self.data_path('whatever')
    
if __name__ == '__main__':
  unit_test.main()
