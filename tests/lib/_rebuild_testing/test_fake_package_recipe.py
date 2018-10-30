#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.testing.unit_test import unit_test
from rebuild.package import artifact_descriptor as AD, package
from rebuild.base import requirement_list as RL

from bes.fs import temp_file, temp_item

from _rebuild_testing.fake_package_recipe import fake_package_recipe as R
from _rebuild_testing.fake_package_recipe_parser import fake_package_recipe_parser as P

class test_fake_package_recipe(unit_test):

  DEBUG = unit_test.DEBUG
  #DEBUG = True

  def test___str__(self):
    r = R(AD('foo', '1.2.3', 0, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18'),
          [
            temp_item('bin/foo.sh', '#!/bin/bash\necho foo\nexit 0\n', 0o755),
            temp_item('bin/bar.sh', '#!/bin/bash\necho bar\nexit 1\n', 0o755),
          ],
          [
            temp_item('foo_env.sh', '#@REBUILD_HEAD@\nexport FOO_ENV=foo\n', 0o644),
            temp_item('bar_env.sh', '#@REBUILD_HEAD@\nexport BAR_ENV=bar\n', 0o644),
          ],
          RL.parse('apple >= 1.2.3 orange >= 6.6.6'),
          { 'prop1': 5, 'prop2': 'hi' },
          {}
    )
    expected = '''fake_package
  metadata
    name foo
    version 1.2.3
    revision 0
    epoch 0
    system linux
    level release
    arch ('x86_64',)
    distro ubuntu
    distro_version 18


  requirements
    all: apple >= 1.2.3
    all: orange >= 6.6.6

  properties
    prop1=5
    prop2=hi'''    
    self.assertMultiLineEqual( expected, str(r) )

  def test_create_package(self):
    recipe = '''
fake_package knife 6.6.6 0 0 linux release x86_64 ubuntu 18
  files
    bin/cut.sh
      \#!/bin/sh
      echo cut.sh: ${1+"$@"} ; exit 0
  c_programs
    bin/cut.exe
      sources
        main.c
          \#include <stdio.h>
          int main(int argc, char* argv[]) {
            char** arg;
            if (argc < 2) {
              fprintf(stderr, "Usage: cut.exe args\\n");
              return 1;
            }
            fprintf(stdout, "cut.exe: ");
            for(arg = argv + 1; *arg != NULL; ++arg) {
              fprintf(stdout, "%s ", *arg);
            }
            fprintf(stdout, "\\n");
            return 0;
          }
  static_c_libs
    lib/libfoo.a
      sources
        foo.c
          int foo(int x) {
            return x + 1;
          }
      headers
        foo.h
          \#ifndef __FOO_H__
          \#define __FOO_H__
          extern int foo(int x);
          \#endif /* __FOO_H__ */

'''

    tmp = temp_file.make_temp_file(suffix = '.tar.gz', delete = not self.DEBUG)
    filename, metadata = self._parse(recipe)[0].create_package(tmp)
    if self.DEBUG:
      print('tmp: %s' % (tmp))

    p = package(tmp)
    self.assertEqual( [
      'bin/cut.exe',
      'bin/cut.sh',
      'lib/libfoo.a',
    ], p.files )
    
  @classmethod
  def _parse(self, text, starting_line_number = 0):
    return P(path.basename(__file__), text, starting_line_number = starting_line_number).parse()
    
if __name__ == '__main__':
  unit_test.main()
