#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.instruction2.instruction_list_parser2 import instruction_list_parser2 as P
from rebuild.instruction2 import instruction2 as I
from bes.text import string_list as SL

class test_instruction_list_parser(unit_test):

  def test_basic(self):
    text='''
liborange1
  CFLAGS
    -I${VAR}/dir
  LDFLAGS
    -L${VAR}/lib
  requires
    libfructose1
'''

    expected = [
      I('liborange1', { 'CFLAGS': SL(['-I${VAR}/dir']), 'LDFLAGS': SL(['-L${VAR}/lib'])  }, set(['libfructose1'])),
    ]
    self.assertEqual( expected, P.parse(text) )

  def test_complete(self):
    text='''
liborange1
  CFLAGS
    -I${VAR}/dir
    -Dfoo="in quotes" -Dbar=666
  LDFLAGS
    -L${VAR}/lib
  LIBS
    -lorange1
  requires
    libfructose1

liborange2
  CFLAGS
    -I${VAR}/dir
    -I${VAR}/dir/caca
  LDFLAGS
    -L${VAR}/lib
  LIBS
    -lorange2
  requires
    libfiber1

orange
  requires
    liborange2
    liborange1
'''

    expected = [
      I('liborange1', { 'CFLAGS': SL(['-I${VAR}/dir', '-Dfoo="in quotes"', '-Dbar=666']), 'LDFLAGS': SL(['-L${VAR}/lib']), 'LIBS': SL(['-lorange1']) }, set(['libfructose1'])),
      I('liborange2', { 'CFLAGS': SL(['-I${VAR}/dir', '-I${VAR}/dir/caca']), 'LDFLAGS': SL(['-L${VAR}/lib']), 'LIBS': SL(['-lorange2']) }, set(['libfiber1'])),
      I('orange', {}, set(['liborange2', 'liborange1'])),
    ]
    self.assertEqual( expected, P.parse(text) )
    
  def xtest_empty(self):
    self.assertEqual( [ ], self._parse('') )
    
  def xtest_parse_simple(self):
    self.assertEqual( [ C('foo', { 'k1': 'v1', 'k2': 'v2 v2a v2b v2c v2d', 'k3': 'v3' }, set()) ],
                      self._parse('name: foo\nk1: v1\nk2: v2 v2a v2b\nv2c v2d\nk3: v3\n') )

  def xtest_parse_two(self):
    self.assertEqual( [ C('foo', { 'k1': 'v1', 'k2': 'v2', 'k3': 'v3' }, set()), C('bar', { 'k4': 'v4', 'k5': 'v5', 'k6': 'v6' }, set()) ],
                      self._parse('name: foo\nk1: v1\nk2: v2\nk3: v3\nname: bar\nk4: v4\nk5: v5\nk6: v6\n') )

  def xtest_parse_one_with_requires(self):
    self.assertEqual( [ C('foo', { 'k1': 'v1' }, set([ 'r1', 'r2'])) ],
                      self._parse('name: foo\nk1: v1\nrequires: r1 r2\n') )

  def xtest_parse_two_with_requires(self):
    self.assertEqual( [ C('n1', { 'k1': 'v1' }, set([ 'r1', 'r2'])), C('n2', { 'k2': 'v2' }, set([ 'r3', 'r4', 'r5'])) ],
                      self._parse('name: n1\nk1: v1\nrequires: r1 r2\nname: n2\nk2: v2\nrequires: r3 r4 r5') )

  @classmethod
  def _parse(self, text):
    return [ i for i in P.parse(text) ]
    
if __name__ == '__main__':
  unit_test.main()
