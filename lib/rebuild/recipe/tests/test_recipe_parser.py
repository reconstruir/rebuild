#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_parser as P, recipe_parser_error as ERR
from rebuild.step_manager import step, step_argspec, step_result

class _step_foo(step):
  def __init__(self):
    super(_step_foo, self).__init__()

  @classmethod
  def argspec(self):
    return {
      'foo_flags': step_argspec.MASKED_KEY_VALUES,
      'foo_env': step_argspec.MASKED_STRING_LIST,
      'foo_script': step_argspec.STRING,
      'need_something': step_argspec.BOOL,
      'patches': step_argspec.MASKED_FILE_LIST,
      'tests': step_argspec.MASKED_FILE_LIST,
    }
    
  def execute(self, script, env, args):
    foo_flags = args.get('foo_flags', [])
    assert isinstance(foo_flags, list)
    foo_env = args.get('foo_env', {})
    assert isinstance(configure_env, dict)
    return step_result(True)

  @classmethod
  def parse_step_args(clazz, script, env, args):
    return clazz.resolve_step_args_env_and_flags(script, args, 'foo_env', 'foo_flags')

class test_recipe_parser(unit_test):

  @classmethod
  def setUpClass(clazz):
    #unit_test.raise_skip('broken')
    pass
  
  def test_simple(self):
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

    _step_foo

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
    class _step_takes_bool(step):
      def __init__(self): super(_step_takes_bool, self).__init__()
      @classmethod
      def argspec(self): return { 'bool_value': step_argspec.BOOL }
      def execute(self, script, env, args): return step_result(True)

    text = '''#!rebuildrecipe
package foo-1.2.3-4
  steps
    _step_takes_bool
      bool_value: True
'''
    r = self._parse(text)
    print('recipe: %s' % (r))
    
  def test_invalid_magic(self):
    with self.assertRaises(ERR) as context:
      self._parse('nomagic')

  @classmethod
  def _parse(self, text):
    return P(text, '<test>').parse()
      
if __name__ == '__main__':
  unit_test.main()
