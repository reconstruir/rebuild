#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.fs.temp_file import temp_file, temp_item

from rebuild._testing.fake_package_source import fake_package_source as S

class test_fake_package_source(unit_test):

  DEBUG = unit_test.DEBUG
  #DEBUG = True

  def test___str__(self):
    s = S('foo.c', r'''\#include <stdio.h>\nint main(int argc, char* argv[]) {\n  printf("foo.c\\n");\n  return 0;\n}\n''')
    expected = r'''foo.c
  \#include <stdio.h>
  int main(int argc, char* argv[]) {
    printf("foo.c\\n");
    return 0;
  }'''
    
    self.assertMultiLineEqual( expected, str(s) )

if __name__ == '__main__':
  unit_test.main()
