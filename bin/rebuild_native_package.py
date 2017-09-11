#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import argparse, os, os.path as path
from rebuild.native_package_manager import native_package_manager as npm
from bes.common import algorithm, dict_util

def main():

  parser = argparse.ArgumentParser()

  subparsers = parser.add_subparsers(help = 'commands', dest = 'command')

  # All
  all_parser = subparsers.add_parser('all', help = 'List all pachages')

  # Installed
  installed_parser = subparsers.add_parser('installed', help = 'Installed archive')
  installed_parser.add_argument('name', action = 'store', help = 'Archive filenames')

  # Info
  info_parser = subparsers.add_parser('info', help = 'Info archive')
  info_parser.add_argument('name', action = 'store', help = 'Archive filenames')

  # contents
  contents_parser = subparsers.add_parser('contents', help = 'List package contents')
  contents_parser.add_argument('name', action = 'store', help = 'The archive')
  contents_parser.add_argument('--levels', '-l',
                               action = 'store',
                               default = None,
                               type = int,
                               help = 'Show only top level directories [ None ]')
  contents_parser.add_argument('--files',
                               action = 'store_true',
                               default = False,
                               help = 'Show only files (no dirs) [ False ]')
  contents_parser.add_argument('--dirs',
                               action = 'store_true',
                               default = False,
                               help = 'Show only dirs (no dirs) [ False ]')

  # Owner
  owner_parser = subparsers.add_parser('owner', help = 'Owner archive contents')
  owner_parser.add_argument('filename', action = 'store', help = 'The archive')

  args = parser.parse_args()
  if args.command == 'all':
    return __command_all()
  elif args.command == 'installed':
    return __command_installed(args.name)
  elif args.command == 'info':
    return __command_info(args.name)
  elif args.command == 'contents':
    return __command_contents(args.name, args.levels, args.files, args.dirs)
  elif args.command == 'owner':
    return __command_owner(args.filename)

  return 0

def __command_all():
  packages = npm.installed_packages()
  for p in packages:
    print(p)
  return 0

def __command_installed(name):
  installed = npm.is_installed(name)
  if not installed:
    return 1
  return 0

def __command_info(name):
  info = npm.package_info(name)
  dict_util.dump(info)
  return 0

def __level_path(p, levels):
  return os.sep.join(p.split(os.sep)[0 : levels])

def __command_contents(name, levels, files_only, dirs_only):
  if files_only and dirs_only:
    raise RuntimeError('Only one of --files or --dirs can be given.')
  if files_only:
    files = npm.package_files(name)
  elif dirs_only:
    files = npm.package_dirs(name)
  else:
    files = npm.package_contents(name)
  if levels is not None:
    files = [ __level_path(p, levels) for p in files ]
    files = algorithm.unique(files)
  for f in files:
    print(f)
  return 0

def __command_owner(filename):
  owner = npm.owner(filename)
  if not owner:
    return 1
  print(owner)
  return 0

if __name__ == '__main__':
  raise SystemExit(main())
