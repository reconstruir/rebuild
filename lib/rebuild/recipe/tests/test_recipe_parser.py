#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.recipe import recipe_parser as P, recipe_parser_error as ERR

class test_recipe_parser(unit_test):

  def test_simple(self):
    text = '''#!rebuildrecipe
#comment

package foo-1.2.3-4
  properties:
    category: lib

  # requirements are nice
  requirements:
    all: bar >= 1.2.8

  build_requirements:
    all: kiwi >= 2.4.6

  steps:
    step_autoconf:
      configure_env:
        all: CFLAGS="$REBUILD_REQUIREMENTS_CFLAGS ${REBUILD_COMPILE_CFLAGS}"
             LDFLAGS=$REBUILD_REQUIREMENTS_LDFLAGS

      configure_flags:
        all: --enable-static --disable-shared
        linux: --with-pic

      patches:
        all: rebuild-foo.patch

      tests:
        desktop: rebuild-foo-test1.cpp
                 rebuild-foo-test2.c
'''
    r = self._parse(text)

  def test_invalid_magic(self):
    with self.assertRaises(ERR) as context:
      self._parse('nomagic')

  @classmethod
  def _parse(self, text):
    return P(text, '<test>').parse()
      
if __name__ == '__main__':
  unit_test.main()
