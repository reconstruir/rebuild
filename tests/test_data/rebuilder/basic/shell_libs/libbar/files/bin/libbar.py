#!/usr/bin/env python

import subprocess, sys

def main():

  libfoo_rv = subprocess.check_output(['libfoo.py', 'a', 'b', 'c']).strip()
  sys.stdout.write(libfoo_rv)
  sys.stdout.write(' # ')
  
  sys.stdout.write('libbar: ')
  for i, arg in enumerate(sys.argv[1:]):
    if i != 0:
      sys.stdout.write(' ')
    sys.stdout.write(arg)
  sys.stdout.write('\n')

if __name__ == '__main__':
  raise SystemExit(main())

