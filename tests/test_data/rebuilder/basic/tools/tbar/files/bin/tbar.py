#!/usr/bin/env python

import subprocess, sys

def main():

  tfoo_rv = subprocess.check_output(['tfoo.py', 'a', 'b', 'c']).strip()
  sys.stdout.write(tfoo_rv)
  sys.stdout.write(' # ')
  
  sys.stdout.write('tbar: ')
  for i, arg in enumerate(sys.argv[1:]):
    if i != 0:
      sys.stdout.write(' ')
    sys.stdout.write(arg)
  sys.stdout.write('\n')

if __name__ == '__main__':
  raise SystemExit(main())

