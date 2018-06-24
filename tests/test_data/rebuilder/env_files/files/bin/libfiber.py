#!/usr/bin/env python

import subprocess, sys

def main():

  libwater_rv = subprocess.check_output(['libwater.py', 'a', 'b', 'c']).strip()
  sys.stdout.write(libwater_rv)
  sys.stdout.write(' # ')
  
  sys.stdout.write('libfiber: ')
  for i, arg in enumerate(sys.argv[1:]):
    if i != 0:
      sys.stdout.write(' ')
    sys.stdout.write(arg)
  sys.stdout.write('\n')

if __name__ == '__main__':
  raise SystemExit(main())

