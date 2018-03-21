#!/usr/bin/env python

import sys

def main():
  sys.stdout.write('tbaz: ')
  for i, arg in enumerate(sys.argv[1:]):
    if i != 0:
      sys.stdout.write(' ')
    sys.stdout.write(arg)
  sys.stdout.write('\n')

if __name__ == '__main__':
  raise SystemExit(main())

