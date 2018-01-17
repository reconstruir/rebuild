#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base import build_level, build_system
from rebuild.sconser import CompileFlags

class TestCompileFlags(unit_test):

  def test_cflags(self):
    flags = CompileFlags(build_level.DEBUG, build_system.LINUX)
    self.assertEqual( [ '-g' ], flags.cflags )

  def test_cflags_append(self):
    flags = CompileFlags(build_level.DEBUG, build_system.LINUX)
    self.assertEqual( [ '-g' ], flags.cflags )
    flags.cflags_append([ '-DFOO' ])
    self.assertEqual( [ '-g', '-DFOO' ], flags.cflags )

  def test_cflags_prepend(self):
    flags = CompileFlags(build_level.DEBUG, build_system.LINUX)
    self.assertEqual( [ '-g' ], flags.cflags )
    flags.cflags_prepend([ '-DFOO' ])
    self.assertEqual( [ '-DFOO', '-g' ], flags.cflags )

  def test_env(self):
    flags = CompileFlags(build_level.DEBUG, build_system.LINUX)
    self.assertEqual( [ '-g' ], flags.cflags )
    flags.cflags_append([ '-DFOO' ])

    self.assertEqual( { 'CFLAGS': '-g -DFOO', 'LDFLAGS': '' }, flags.env )

if __name__ == '__main__':
  unit_test.main()
