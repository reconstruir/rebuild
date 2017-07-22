#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from rebuild import build_target, build_type, CompileFlags, System

class TestCompileFlags(unittest.TestCase):

  def test_cflags(self):
    flags = CompileFlags(build_type.DEBUG, System.LINUX)
    self.assertEqual( [ '-g' ], flags.cflags )

  def test_cflags_append(self):
    flags = CompileFlags(build_type.DEBUG, System.LINUX)
    self.assertEqual( [ '-g' ], flags.cflags )
    flags.cflags_append([ '-DFOO' ])
    self.assertEqual( [ '-g', '-DFOO' ], flags.cflags )

  def test_cflags_prepend(self):
    flags = CompileFlags(build_type.DEBUG, System.LINUX)
    self.assertEqual( [ '-g' ], flags.cflags )
    flags.cflags_prepend([ '-DFOO' ])
    self.assertEqual( [ '-DFOO', '-g' ], flags.cflags )

  def test_env(self):
    flags = CompileFlags(build_type.DEBUG, System.LINUX)
    self.assertEqual( [ '-g' ], flags.cflags )
    flags.cflags_append([ '-DFOO' ])

    self.assertEqual( { 'CFLAGS': '-g -DFOO', 'LDFLAGS': '' }, flags.env )

if __name__ == '__main__':
  unittest.main()
