#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import argparse, os, os.path as path, sys
from bes.fs import file_util
from rebuild import binary_format_macho

def main():

  parser = argparse.ArgumentParser()

  subparsers = parser.add_subparsers(help = 'commands', dest = 'command')

  # Magic
  magic_parser = subparsers.add_parser('magic', help = 'Print Mach-O file magic numbers')
  magic_parser.add_argument('files', action = 'store', nargs = '+', help = 'Files to check')

  magic_parser.add_argument('--dest-dir',
                              '-d',
                              action = 'store',
                              default = os.getcwd(),
                              help = 'Destination directory [ cwd ]')

  # Info
  info_parser = subparsers.add_parser('info', help = 'Print Mach-O file info')
  info_parser.add_argument('files', action = 'store', nargs = '+', help = 'Files to check')

  info_parser.add_argument('--dest-dir',
                              '-d',
                              action = 'store',
                              default = os.getcwd(),
                              help = 'Destination directory [ cwd ]')

  args = parser.parse_args()

  macho = binary_format_macho()
  
  if args.command == 'info':
    return _command_info(macho, args.files)
  elif args.command == 'magic':
    return _command_magic(macho, args.files)

  return 0

def _command_magic(macho, files):
  abs_files = file_util.make_paths_absolute(files)
  for filename, abs_filename in zip(files, abs_files):
    magic = macho.read_magic(abs_filename)
    print('%8s %s' % (magic, filename))
  return 0

def _command_info(macho, files):
  abs_files = file_util.make_paths_absolute(files)
  print('%-8s %-8s %-13s %s' % ('MAGIC', 'CPU TYPE', 'FILE TYPE', 'FILENAME'))
  for filename, abs_filename in zip(files, abs_files):
    info = macho.read_info(abs_filename)
    if info:
      for obj in info.objects:
        print('%-8s %-8s %-11s %s' % (obj.magic, obj.cpu_type, obj.file_type, filename))
  return 0

if __name__ == '__main__':
  sys.exit(main())
