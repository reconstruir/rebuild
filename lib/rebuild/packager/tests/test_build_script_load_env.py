#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from rebuild.packager.build_script_load_env import build_script_load_env
from rebuild import build_target, System

class test_build_script_load_env(unittest.TestCase):

  def test_args(self):
    bi = build_target(System.LINUX)
    bse = build_script_load_env(bi)
    a = bse.args(foo = 5, bar = 'hello')
    self.assertEqual( { 'foo': 5, 'bar': 'hello' }, a )
    self.assertEqual( System.LINUX, bse.system )

if __name__ == '__main__':
  unittest.main()
