#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.testing.unit_test import unit_test
from bes.archive.archiver import archiver

from rebuild.package.package import package
from rebuild.base.artifact_descriptor import artifact_descriptor as AD
from rebuild.base.requirement_list import requirement_list as RL

from bes.fs.temp_file import temp_file, temp_item

from rebuild._testing.fake_package_recipe import fake_package_recipe as R
from rebuild._testing.fake_package_recipe_parser import fake_package_recipe_parser as P
from rebuild._testing.fake_package_recipes import fake_package_recipes as RECIPES

class test_fake_package_recipe(unit_test):

  DEBUG = unit_test.DEBUG
  #DEBUG = True

  def test___str__(self):
    r = R(AD('foo', '1.2.3', 0, 0, 'linux', 'release', 'x86_64', 'ubuntu', '18', ''),
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
    expected = r'''fake_package
  metadata
    name foo
    version 1.2.3
    revision 0
    epoch 0
    system linux
    level release
    arch ('x86_64',)
    distro ubuntu
    distro_version_major 18
    distro_version_minor 


  requirements
    all: apple >= 1.2.3
    all: orange >= 6.6.6

  properties
    prop1=5
    prop2=hi'''    
    self.assertMultiLineEqual( expected, str(r) )

  def test_create_package(self):
    recipe = r'''
fake_package knife 6.6.6 0 0 linux release x86_64 ubuntu 18 none
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
    bin/links_with_static.exe
      sources
        main.c
          \#include <libfoo_static.h>
          \#include <stdio.h>
          int main() {
            printf("%d\\n", foo_static(10));
            return 0;
          }
      ldflags
        -lfoo_static
    bin/links_with_shared.exe
      sources
        main.c
          \#include <libfoo_shared.h>
          \#include <stdio.h>
          int main() {
            printf("%d\\n", foo_shared(20));
            return 0;
          }
      ldflags
        -lfoo_shared
  static_c_libs
    lib/libfoo_static.a
      sources
        foo.c
          \#include <libfoo_static.h>
          const int FOO_STATIC_MAGIC_NUMBER = 1;
          int foo_static(int x) {
            return x + FOO_STATIC_MAGIC_NUMBER;
          }
      headers
        include/libfoo_static.h
          \#ifndef __FOO_STATIC_H__
          \#define __FOO_STATIC_H__
          extern const int FOO_STATIC_MAGIC_NUMBER;
          extern int foo_static(int x);
          \#endif /* __FOO_STATIC_H__ */
  shared_c_libs
    lib/libfoo_shared.so
      sources
        foo2.c
          \#include <libfoo_shared.h>
          int foo_shared(int x) {
            return x + FOO_SHARED_MAGIC_NUMBER;
          }
      headers
        include/libfoo_shared.h
          \#ifndef __FOO_SHARED_H__
          \#define __FOO_SHARED_H__
          \#define FOO_SHARED_MAGIC_NUMBER 2
          extern int foo_shared(int x);
          \#endif /* __FOO_SHARED_H__ */

'''

    tmp = temp_file.make_temp_file(suffix = '.tar.gz', delete = not self.DEBUG)
    filename, metadata = self._parse(recipe)[0].create_package(tmp, debug = self.DEBUG)
    if self.DEBUG:
      print('tmp:\n%s' % (tmp))

    # Assert that the package has exactly the members expected
    self.assertEqual( [
      'files/bin/cut.exe',
      'files/bin/cut.sh',
      'files/bin/links_with_shared.exe',
      'files/bin/links_with_static.exe',
      'files/include/libfoo_shared.h',
      'files/include/libfoo_static.h',
      'files/lib/libfoo_shared.so',
      'files/lib/libfoo_static.a',
      'metadata/metadata.json',
      ], archiver.members(tmp) )
      
    p = package(tmp)
    self.assertEqual( [
      'bin/cut.exe',
      'bin/cut.sh',
      'bin/links_with_shared.exe',
      'bin/links_with_static.exe',
      'include/libfoo_shared.h',
      'include/libfoo_static.h',
      'lib/libfoo_shared.so',
      'lib/libfoo_static.a',
    ], p.files )
    
  @classmethod
  def _parse(self, text, starting_line_number = 0):
    return P(path.basename(__file__), text, starting_line_number = starting_line_number).parse()
    
if __name__ == '__main__':
  unit_test.main()
