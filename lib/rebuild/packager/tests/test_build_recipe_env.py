#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.packager.build_recipe_env import build_recipe_env

class test_build_recipe_env(unit_test):

  def test_args(self):
    bse = build_recipe_env()
    a = bse.args(foo = 5, bar = 'hello')
    self.assertEqual( { 'foo': 5, 'bar': 'hello' }, a )

if __name__ == '__main__':
  unit_test.main()
