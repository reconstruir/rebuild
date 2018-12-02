#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect, os.path as path
from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe, recipe_parser as P, recipe_error as ERR, recipe_step as RS, testing_recipe_load_env
from rebuild.step import compound_step, step, step_result
from rebuild.base import build_target
from bes.key_value import key_value as KV, key_value_list as KVL
from bes.fs import file_util, temp_file
from test_steps import *

from _rebuild_testing.recipe_parser_testing import recipe_parser_testing

class test_recipe_parser(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/recipe_parser'

  TEST_ENV = testing_recipe_load_env()
  
  @classmethod
  def _parse(self, text, starting_line_number = 0):
    return P(path.basename(__file__), text, starting_line_number = starting_line_number).parse()

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
package foo 1.2.3 4
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )

  def test_package_version_space(self):
    frame = inspect.getframeinfo(inspect.currentframe())
    text = '''!rebuild.recipe!
package foo 1.2.3 4
'''
    r = self._parse(text, frame.lineno)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    
  def test_step_value_bool_no_mask(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4
  steps
    step_takes_bool
      bool_value: True
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertMultiLineEqual( 'step_takes_bool\n    bool_value: True', str(r[0].steps[0]) )

  def test_step_value_bool_empty_value(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4
  steps
    step_takes_bool
      bool_value:
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertMultiLineEqual( 'step_takes_bool\n    bool_value:', str(r[0].steps[0]) )
    
  def test_step_value_bool_with_mask(self):
    self.maxDiff = None
    
    text = '''!rebuild.recipe!
package foo 1.2.3 4
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
package foo 1.2.3 4
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
package foo 1.2.3 4
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
package foo 1.2.3 4
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
package foo 1.2.3 4
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
package foo 1.2.3 4
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
package foo 1.2.3 4
  steps
    step_takes_string
      string_value: "my string # with a hash"
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_string\n    string_value: "my string # with a hash"', str(r[0].steps[0]) )
    
  def test_step_value_string_listx(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4
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
package foo 1.2.3 4
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
package foo 1.2.3 4
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
package foo 1.2.3 4
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
package foo 1.2.3 4
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
package foo 1.2.3 4
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
    self.assertMultiLineEqual( expected, str(r[0].steps[0]) )

  def test_takes_all(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4
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
    self.assertMultiLineEqual( expected, str(r[0].steps[0]) )
    
  def test_compound_step(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4
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
    self.assertMultiLineEqual( expected, str(r[0].steps[0]) )
    
  def test_multiple_steps(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4
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
    self.maxDiff = None
    text = '''!rebuild.recipe!
#comment

package foo 1.2.3 4
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
package foo 1.2.3 4
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

  def test_step_inline_python_code(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4
  steps
    test_inline_step1
      bool_value: True

    test_inline_step2
      bool_value: True

  python_code
    > from rebuild.step import step
      class test_inline_step1(step):
        def __init__(self):
          super(test_inline_step1, self).__init__()
        @classmethod
        def define_args(clazz):
          return 'bool_value bool'
        def execute(self, script, env, args):
          return self.result(True)
      class test_inline_step2(step):
        def __init__(self):
          super(test_inline_step2, self).__init__()
        @classmethod
        def define_args(clazz):
          return 'bool_value bool'
        def execute(self, script, env, args):
          return self.result(True)

'''

    r = P(self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 'test_inline_step1\n    bool_value: True', str(r[0].steps[0]) )
    self.assertEqual( 'test_inline_step2\n    bool_value: True', str(r[0].steps[1]) )
    print(str(r[0]))
    
  def test_step_value_hook(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4
  steps
    step_takes_hook
      hook_value
        all: test_hook1
          class test_hook1(hook):
            def execute(self, script, env, args):
              return self.result(True)
        all: test_hook2
          class test_hook2(hook):
            def execute(self, script, env, args):
              return self.result(True)
'''
    r = P(self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 1, len(r[0].steps) )
#    self.assertMultiLineEqual( 'step_takes_hook\n  hook_value\n    all: test_hook1\n    all: test_hook2', str(r[0].steps[0]) )
#    actual_hook1_filename = r[0].steps[0].values[0].values[0].value[0].filename
#    actual_hook2_filename = r[0].steps[0].values[0].values[1].value[0].filename
#    self.assertEqual( expected_hook1_filename, actual_hook1_filename )
#    self.assertEqual( expected_hook2_filename, actual_hook2_filename )
    
  def test_step_value_hook_with_mask(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4
  steps
    step_takes_hook
      hook_value
        linux: test_hook3
          class test_hook3(hook):
            def execute(self, script, env, args):
              return self.result(True)
        linux: test_hook4
          class test_hook4(hook):
            def execute(self, script, env, args):
              return self.result(True)
'''
    r = P(self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertEqual( 1, len(r[0].steps) )
#    self.assertMultiLineEqual( 'step_takes_hook\n  hook_value\n    linux: test_hook3\n    linux: test_hook4', str(r[0].steps[0]) )
 #   actual_hook3_filename = r[0].steps[0].values[0].values[0].value[0].filename
 #   actual_hook4_filename = r[0].steps[0].values[0].values[1].value[0].filename

  def test_step_value_file_list(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4

  steps
    step_takes_file_list
      file_list_value: test_file1.txt test_file2.txt
'''
    r = P(self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_file_list\n    file_list_value: test_file1.txt test_file2.txt', str(r[0].steps[0]) )

  def test_step_value_file_list_with_properties(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4

  steps
    step_takes_file_list
      file_list_value: test_file1.txt test_file2.txt foo=5 bar=6
'''
    r = P(self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_file_list\n    file_list_value: test_file1.txt test_file2.txt foo=5 bar=6', str(r[0].steps[0]) )

  def xtest_step_value_file_list_with_properties_multi_line(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4

  steps
    step_takes_file_list
      file_list_value: test_file1.txt test_file2.txt foo=5
                       bar=6
'''
    r = P(self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_file_list\n    file_list_value: test_file1.txt test_file2.txt foo=5 bar=6', str(r[0].steps[0]) )
    
  def test_step_value_file(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4

  steps
    step_takes_file
      file_value: test_file1.txt
'''
    r = P(self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_file\n    file_value: test_file1.txt', str(r[0].steps[0]) )

  def test_step_value_file_with_values(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4

  steps
    step_takes_file
      file_value: test_file1.txt foo=1 bar=2 baz=\"hello kiwi\"
'''
    r = P(self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_file\n    file_value: test_file1.txt foo=1 bar=2 baz=\"hello kiwi\"', str(r[0].steps[0]) )

  def test_step_value_install_file(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4

  steps
    step_takes_install_file
      install_file_value: test_file1.txt etc/foo/f1.txt
'''
    r = P(self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_install_file\n    install_file_value: test_file1.txt etc/foo/f1.txt', str(r[0].steps[0]) )

  def test_step_value_install_file_many(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4

  steps
    step_takes_install_file
      install_file_value
        all: test_file1.txt etc/foo/f1.txt
        all: test_file2.txt etc/foo/f2.txt
'''
    r = P(self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_install_file\n  install_file_value\n    all: test_file1.txt etc/foo/f1.txt\n    all: test_file2.txt etc/foo/f2.txt', str(r[0].steps[0]) )


  def test_step_comments(self):
    text = '''!rebuild.recipe!
# comment
package foo 1.2.3 4 # comment
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
package foo 1.2.3 4
  steps
    step_takes_bool
'''
    r = self._parse(text)
    self.assertEqual( 1, len(r) )
    self.assertEqual( 'foo', r[0].descriptor.name )
    self.assertEqual( ( '1.2.3', 4, 0 ), r[0].descriptor.version )
    self.assertMultiLineEqual( 'step_takes_bool', str(r[0].steps[0]) )

  def test_step_git_address(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4

  steps
    step_takes_git_address
      git_address_value: test_file1.txt test_file2.txt
'''
    r = P(self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )
    self.assertMultiLineEqual( 'step_takes_git_address\n    git_address_value: test_file1.txt test_file2.txt', str(r[0].steps[0]) )

  def test_step_value_commented_out(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4
  steps
    step_takes_file_list
      file_list_value
        all: test_file1.txt
        all: test_file2.txt
'''
    r = P(self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )

    step1 = r[0].steps[0]
    values = step1.resolve_values({}, self.TEST_ENV)
    files = values['file_list_value']
    self.assertEqual( 2, len(files) )
    self.assertEqual( self.data_path('test_file1.txt'), files[0].filename )
    self.assertEqual( self.data_path('test_file2.txt'), files[1].filename )

    text = '''!rebuild.recipe!
package foo 1.2.3 4
  steps
    step_takes_file_list
      file_list_value
        all: #test_file1.txt
        all: test_file2.txt
'''
    r = P(self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )

    step1 = r[0].steps[0]
    values = step1.resolve_values({}, self.TEST_ENV)
    files = values['file_list_value']
    self.assertEqual( 1, len(files) )
    self.assertMultiLineEqual( self.data_path('test_file2.txt'), files[0].filename )

  def test_step_value_file_list_empty(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4
  steps
    step_takes_file_list
      file_list_value
'''
    r = P(self._filename_for_parser(), text).parse()
    self.assertEqual( 1, len(r) )
    self.assertEqual( 1, len(r[0].steps) )

    step1 = r[0].steps[0]
    values = step1.resolve_values({}, self.TEST_ENV)
    self.assertEqual( None, values['file_list_value'] )
    
  def _filename_for_parser(self):
    'Return a fake filename for parser.  Some values need it to find files relatively to filename.'
    return self.data_path('whatever')

class test_recipe_step_values(unit_test):
  
  def xtest_step_value_string_list(self):
    text = '''!rebuild.recipe!
package foo 1.2.3 4
  steps
    step_takes_string_list
      string_list_value: a b "x y"
                         c d "e f"
'''
    r = self._parse(text)
    r2 =  r[0].steps[0].values[0].values
    print('R2: %s' % (r2[0].value))
#    print('FUCK: %s' % (type(r[0].steps[0].values[0].values)))
#    self.assertEqual( [
#      ( None, True ),
#    ], [ tuple(x) for x in r[0].steps[0].values[0].values ] )
    
#  steps  
#    step_autoconf
#      configure_env
#        all: a=1
#             b=1

class test_recipe_step_value_bool(unit_test):
  
  def test_inline(self):
    value_text = '''\
bool_value: True
'''
    values = recipe_parser_testing.parse_trivial_recipe('foo', '1.2.3.4', 'step_takes_bool', value_text)
    self.assertEqual( [
      ( None, True ),
    ], [ tuple(x) for x in values ] )

  def test_masked(self):
    value_text = '''\
bool_value
  all: True
'''
    values = recipe_parser_testing.parse_trivial_recipe('foo', '1.2.3.4', 'step_takes_bool', value_text)
    self.assertEqual( [
      ( 'all', True ),
    ], [ tuple(x) for x in values ] )

  def test_masked_multiple_values(self):
    value_text = '''\
bool_value
  all: True
  android: False
'''
    values = recipe_parser_testing.parse_trivial_recipe('foo', '1.2.3.4', 'step_takes_bool', value_text)
    self.assertEqual( [
      ( 'all', True ),
      ( 'android', False ),
    ], [ tuple(x) for x in values ] )

  def test_mixed(self):
    value_text = '''\
bool_value: True
  all: True
  android: False
'''
    values = recipe_parser_testing.parse_trivial_recipe('foo', '1.2.3.4', 'step_takes_bool', value_text)
    self.assertEqual( [
      ( None, True ),
      ( 'all', True ),
      ( 'android', False ),
    ], [ tuple(x) for x in values ] )

class test_recipe_step_value_string(unit_test):
  
  def test_inline(self):
    value_text = '''\
string_value: kiwi
'''
    values = recipe_parser_testing.parse_trivial_recipe('foo', '1.2.3.4', 'step_takes_string', value_text)
    self.assertEqual( [
      ( None, 'kiwi' ),
    ], [ tuple(x) for x in values ] )

  def test_colon_inline(self):
    value_text = '''\
string_value: a:b:c
'''
    values = recipe_parser_testing.parse_trivial_recipe('foo', '1.2.3.4', 'step_takes_string', value_text)
    self.assertEqual( [
      ( None, 'a:b:c' ),
    ], [ tuple(x) for x in values ] )

  def xxtest_inline_multiline(self):
    value_text = '''\
string_value: kiwi
              foo:
'''
    values = recipe_parser_testing.parse_trivial_recipe('foo', '1.2.3.4', 'step_takes_string', value_text)
    self.assertEqual( [
      ( None, 'kiwi\nfoo' ),
    ], [ tuple(x) for x in values ] )

    
  def test_masked(self):
    value_text = '''\
string_value
  all: kiwi
'''
    values = recipe_parser_testing.parse_trivial_recipe('foo', '1.2.3.4', 'step_takes_string', value_text)
    self.assertEqual( [
      ( 'all', 'kiwi' ),
    ], [ tuple(x) for x in values ] )

    
  def test_masked_multiple_values(self):
    value_text = '''\
string_value
  all: kiwi
  android: orange
'''
    values = recipe_parser_testing.parse_trivial_recipe('foo', '1.2.3.4', 'step_takes_string', value_text)
    self.assertEqual( [
      ( 'all', 'kiwi' ),
      ( 'android', 'orange' ),
    ], [ tuple(x) for x in values ] )

  def test_mixed(self):
    value_text = '''\
string_value: kiwi
  all: apple
  android: orange
'''
    values = recipe_parser_testing.parse_trivial_recipe('foo', '1.2.3.4', 'step_takes_string', value_text)
    self.assertEqual( [
      ( None, 'kiwi' ),
      ( 'all', 'apple' ),
      ( 'android', 'orange' ),
    ], [ tuple(x) for x in values ] )

class test_recipe_step_value_int(unit_test):
  
  def test_inline(self):
    value_text = '''\
int_value: 666
'''
    values = recipe_parser_testing.parse_trivial_recipe('foo', '1.2.3.4', 'step_takes_int', value_text)
    self.assertEqual( [
      ( None, 666 ),
    ], [ tuple(x) for x in values ] )

  def test_masked(self):
    value_text = '''\
int_value
  all: 666
'''
    values = recipe_parser_testing.parse_trivial_recipe('foo', '1.2.3.4', 'step_takes_int', value_text)
    self.assertEqual( [
      ( 'all', 666 ),
    ], [ tuple(x) for x in values ] )

  def test_masked_multiple_values(self):
    value_text = '''\
int_value
  all: 666
  android: 777
'''
    values = recipe_parser_testing.parse_trivial_recipe('foo', '1.2.3.4', 'step_takes_int', value_text)
    self.assertEqual( [
      ( 'all', 666 ),
      ( 'android', 777 ),
    ], [ tuple(x) for x in values ] )

  def test_mixed(self):
    value_text = '''\
int_value: 666
  all: 999
  android: 777
'''
    values = recipe_parser_testing.parse_trivial_recipe('foo', '1.2.3.4', 'step_takes_int', value_text)
    self.assertEqual( [
      ( None, 666 ),
      ( 'all', 999 ),
      ( 'android', 777 ),
    ], [ tuple(x) for x in values ] )
    
if __name__ == '__main__':
  unit_test.main()
