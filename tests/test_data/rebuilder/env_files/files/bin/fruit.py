#!/usr/bin/env python

import subprocess, sys

def main():

  water_rv = subprocess.check_output(['water.py', 'a', 'b', 'c']).strip()
  sys.stdout.write(water_rv)
  sys.stdout.write(' # ')
  
  fiber_rv = subprocess.check_output(['fiber.py', 'a', 'b', 'c']).strip()
  sys.stdout.write(fiber_rv)
  sys.stdout.write(' # ')
  
  sys.stdout.write('fruit: ')
  for i, arg in enumerate(sys.argv[1:]):
    if i != 0:
      sys.stdout.write(' ')
    sys.stdout.write(arg)
  sys.stdout.write('\n')

if __name__ == '__main__':
  raise SystemExit(main())
