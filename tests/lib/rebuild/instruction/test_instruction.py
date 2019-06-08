#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.instruction.instruction import instruction as I
from bes.text.string_list import string_list as SL

class test_instruction(unit_test):

  def test___str__(self):
    i = I('orange', { 'x': SL([ '5' ]), 'y': SL([ 'hi' ]) }, set([ 'fructose', 'fiber' ]))
    expected = '''\
orange
  x
    5
  y
    hi
  requires
    fiber
    fructose\
'''
    self.assertMultiLineEqual( expected, str(i) )

  def test_parse(self):
    text = '''
liborange1
  CFLAGS
    -I${REBUILD_PACKAGE_PREFIX}/include
    -Dfoo="something in quotes"
  LDFLAGS
    -L${REBUILD_PACKAGE_PREFIX}/lib
  LIBS
    -lorange1
  requires
    libfructose1

liborange2
  CFLAGS
    -I${REBUILD_PACKAGE_PREFIX}/include
    -I${REBUILD_PACKAGE_PREFIX}/include/caca
  LDFLAGS
    -L${REBUILD_PACKAGE_PREFIX}/lib
  LIBS
    -lorange2
  requires
    libfiber1

orange
  requires
    liborange1
    liborange2
'''

if __name__ == '__main__':
  unit_test.main()
