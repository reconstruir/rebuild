#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import argparse, os, os.path as path
from rebuild.toolchain import library

def main():

  parser = argparse.ArgumentParser()

  parser.add_argument('--recursive', '-r',
                      action = 'store_true',
                      default = False,
                      help = 'List libraries recursively [ False ]')
  parser.add_argument('files', action = 'store', nargs = '+', help = 'Files to ldd')

  args = parser.parse_args()

  if len(args.files) == 1:
    deps = _deps(args.files[0], args.recursive)
    if deps != None:
      for d in deps:
        print(d)
  else:
    for f in args.files:
      deps = _deps(f, args.recursive)
      if deps != None:
        print(f)
        for d in deps:
          print(('  %s' % (d)))

  return 0

def _deps(filename, recursive):
  if recursive:
    return library.dependencies_recursive(filename)
  else:
    return library.dependencies(filename)

if __name__ == '__main__':
  raise SystemExit(main())
