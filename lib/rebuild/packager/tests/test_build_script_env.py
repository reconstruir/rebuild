#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from rebuild.packager.build_script_env import build_script_env
from rebuild import build_target, System

class Testbuild_script_env(unittest.TestCase):

  def test_args(self):
    bi = build_target(System.LINUX)
    bse = build_script_env(bi)
    a = bse.args(foo = 5, bar = 'hello')
    self.assertEqual( { 'foo': 5, 'bar': 'hello' }, a )
    self.assertEqual( System.LINUX, bse.system )

if __name__ == '__main__':
  unittest.main()
