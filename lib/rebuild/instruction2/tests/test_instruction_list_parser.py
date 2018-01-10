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
    
  def test_empty(self):
    self.assertEqual( [ ], P.parse('') )
    
if __name__ == '__main__':
  unit_test.main()
