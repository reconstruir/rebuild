#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class fake_package_recipes(object):

  WATER = 'fake_package water 1.0.0 0 0 linux release x86_64 ubuntu 18 none'

  APPLE = '''\
fake_package apple 1.2.3 1 0 linux release x86_64 ubuntu 18 none
  requirements
    fruit >= 1.0.0
'''

  TWO_APPLES = '''\
fake_package apple 1.2.3 1 0 linux release x86_64 ubuntu 18 none
  requirements
    fruit >= 1.0.0
fake_package apple 1.2.4 1 0 linux release x86_64 ubuntu 18 none
  requirements
    fruit >= 1.0.0
'''
  
  FOODS = r'''
fake_package water 1.0.0 0 0 linux release x86_64 ubuntu 18 none

fake_package water 1.0.0 1 0 linux release x86_64 ubuntu 18 none

fake_package water 1.0.0 2 0 linux release x86_64 ubuntu 18 none

fake_package fiber 1.0.0 0 0 linux release x86_64 ubuntu 18 none

fake_package citrus 1.0.0 2 0 linux release x86_64 ubuntu 18 none

fake_package fructose 3.4.5 6 0 linux release x86_64 ubuntu 18 none

fake_package mercury 1.2.8 0 0 linux release x86_64 ubuntu 18 none

fake_package mercury 1.2.8 1 0 linux release x86_64 ubuntu 18 none

fake_package mercury 1.2.9 0 0 linux release x86_64 ubuntu 18 none

fake_package arsenic 1.2.9 0 0 linux release x86_64 ubuntu 18 none

fake_package arsenic 1.2.9 1 0 linux release x86_64 ubuntu 18 none

fake_package arsenic 1.2.10 0 0 linux release x86_64 ubuntu 18 none

fake_package apple 1.2.3 1 0 linux release x86_64 ubuntu 18 none
  requirements
    fruit >= 1.0.0

fake_package fruit  1.0.0 0 0 linux release x86_64 ubuntu 18 none
  requirements
    fructose >= 3.4.5-6
    fiber >= 1.0.0-0
    water >= 1.0.0-0

fake_package pear 1.2.3 1 0 linux release x86_64 ubuntu 18 none
  requirements
    fruit >= 1.0.0

fake_package orange 6.5.4 3 0 linux release x86_64 ubuntu 18 none
  requirements
    fruit >= 1.0.0
    citrus >= 1.0.0

fake_package orange_juice 1.4.5 0 0 linux release x86_64 ubuntu 18 none
  requirements
    orange >= 6.5.4-3

fake_package pear_juice 6.6.6 0 0 linux release x86_64 ubuntu 18 none
  requirements
    pear >= 1.2.3-1
    
fake_package smoothie 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  requirements
    orange >= 6.5.4-3
    pear >= 1.2.3-1
    apple >= 1.2.3-1

fake_package knife 1.0.0 0 0 linux release x86_64 ubuntu 18 none
  files
    bin/cut.sh
      \#!/bin/bash
      echo cut ; exit 0
'''
  
  KNIFE = r'''
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

  env_files
    knife_env.sh
      \#@REBUILD_HEAD@
      bes_env_path_append PATH ${REBUILD_STUFF_DIR}/bin
      bes_env_path_append PYTHONPATH ${REBUILD_STUFF_DIR}/lib/python
      bes_env_path_append LD_LIBRARY_PATH ${REBUILD_STUFF_DIR}/lib
      \#@REBUILD_TAIL@
'''
