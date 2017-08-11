#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import argparse, os, os.path as path, sys

from bes.fs import file_util
from bes.archive import archiver
from rebuild import Patch, TarballUtil, package_descriptor

def main():

  parser = argparse.ArgumentParser()

  subparsers = parser.add_subparsers(help = 'commands', dest = 'command')

  # Extract
  extract_parser = subparsers.add_parser('extract', help = 'Extract archive')
  extract_parser.add_argument('archives', action = 'store', nargs = '+', help = 'Archive filenames')

  extract_parser.add_argument('--dest-dir',
                              '-d',
                              action = 'store',
                              default = os.getcwd(),
                              help = 'Destination directory [ cwd ]')
  extract_parser.add_argument('--base-dir',
                              '-b',
                              action = 'store',
                              default = None,
                              help = 'Base dir to add to extracted archive [ None ]')
  extract_parser.add_argument('--strip-common-base',
                              '-s',
                              action = 'store_true',
                              default = False,
                              help = 'Whether to strip a common base [ False ]')

  # Create
  create_parser = subparsers.add_parser('create', help = 'Create archive')
  create_parser.add_argument('root_dir', action = 'store', help = 'Directory to archive')
  create_parser.add_argument('name', action = 'store', help = 'Archive name')
  create_parser.add_argument('version', action = 'store', help = 'Archive version')
  create_parser.add_argument('--revision',
                             '-r',
                             action = 'store',
                             default = '1',
                             help = 'Revision for archive [ 1 ]')
  
  # Find
  find_parser = subparsers.add_parser('find', help = 'Find archive')

  find_parser.add_argument('root_dir',
                           action = 'store',
                           help = 'Root directory to look for archives')

  find_parser.add_argument('name',
                           action = 'store',
                           default = None,
                           help = 'Name to look for')

  find_parser.add_argument('version',
                           action = 'store',
                           default = None,
                           help = 'Version to look for')

  # Download
  download_parser = subparsers.add_parser('download', help = 'Download tarballs from github.')

  download_parser.add_argument('name',
                               action = 'store',
                               default = None,
                               help = 'Name of the project')

  download_parser.add_argument('url',
                               action = 'store',
                               help = 'Github url')

  download_parser.add_argument('tag',
                               action = 'store',
                               default = None,
                               help = 'git tag to download')

  # Print
  print_parser = subparsers.add_parser('print', help = 'Print archive contents')
  print_parser.add_argument('filename', action = 'store', help = 'The archive')

  # Cat
  cat_parser = subparsers.add_parser('cat', help = 'Cat archive contents')
  cat_parser.add_argument('archive', action = 'store', help = 'The archive')
  cat_parser.add_argument('members', action = 'store', nargs = '+', help = 'The members to cat')

  # Help
  help_parser = subparsers.add_parser('help', help = 'Give the output of configure --help for the autoconf packages.')
  help_parser.add_argument('archive', action = 'store', help = 'The archive')

  # Grep
  grep_parser = subparsers.add_parser('grep', help = 'Grep the contents of the archive using ag (silver searcher).')
  grep_parser.add_argument('archive', action = 'store', help = 'The archive')
  grep_parser.add_argument('pattern', action = 'store', help = 'The pattern to search for')

  # Patch_Prepare
  patch_prepare_parser = subparsers.add_parser('patch_prepare', help = 'Prepare to make patches.')
  patch_prepare_parser.add_argument('archive', action = 'store', help = 'The archive')
  patch_prepare_parser.add_argument('--dest-dir',
                                    '-d',
                                    action = 'store',
                                    default = path.join(os.getcwd(), 'patch_tmp'),
                                    help = 'Temp dir to work on patches [ cwd/patch_tmp ]')
  # Patch_Make
  patch_make_parser = subparsers.add_parser('patch_make', help = 'Make to make patches.')
  patch_make_parser.add_argument('working_dir', action = 'store', help = 'The archive')

  # Info
  info_parser = subparsers.add_parser('info', help = 'Print archive info')
  info_parser.add_argument('filename', action = 'store', help = 'The archive')

  # Patch
  patch_parser = subparsers.add_parser('patch', help = 'Patch archive')

  patch_parser.add_argument('patches', action = 'store', nargs = '+', help = 'Patches to apply')

  patch_parser.add_argument('--backup',
                            '-b',
                            action = 'store_true',
                            default = False,
                            help = 'Whether to make a backup [ False ]')

  patch_parser.add_argument('--strip',
                            '-p',
                            action = 'store',
                            default = 0,
                            type = int,
                            help = 'How much prefix to strip [ 0 ]')

  patch_parser.add_argument('--cwd',
                            '-C',
                            action = 'store',
                            default = os.getcwd(),
                            type = str,
                            help = 'How much prefix to strip [ 0 ]')

  patch_parser.add_argument('--posix',
                            action = 'store_true',
                            default = False,
                            help = 'Whether to turn posix flag on [ False ]')

  # Diff
  diff_parser = subparsers.add_parser('diff', help = 'Diff the contents of the archive using ag (silver searcher).')
  diff_parser.add_argument('archive1', action = 'store', help = 'The first archive')
  diff_parser.add_argument('archive2', action = 'store', help = 'The second archive')

  args = parser.parse_args()

  if args.command == 'print':
    return _command_print(args.filename)
  elif args.command == 'cat':
    return _command_cat(args.archive, args.members)
  elif args.command == 'help':
    return _command_help(args.archive)
  elif args.command == 'grep':
    return _command_grep(args.archive, args.pattern)
  elif args.command == 'patch_prepare':
    return _command_patch_prepare(args.archive, args.dest_dir)
  elif args.command == 'patch_make':
    return _command_patch_make(args.working_dir)
  elif args.command == 'info':
    return _command_info(args.filename)
  elif args.command == 'extract':
    return _command_extract(file_util.make_paths_absolute(args.archives),
                            args.dest_dir,
                            args.base_dir,
                            args.strip_common_base)
  elif args.command == 'create':
    return _command_create(args.root_dir,
                           args.name,
                           args.version,
                           args.revision)
  elif args.command == 'patch':
    return _command_patch(args)
  elif args.command == 'find':
    return _command_find(args.root_dir, args.name, args.version)
  elif args.command == 'download':
    return _command_download(args.name, args.url, args.tag)
  elif args.command == 'diff':
    return _command_diff(args.archive1, args.archive2)

  return 0

def _command_print(filename):
  members = archiver.members(filename)
  for member in members:
    print member
  return 0

def _command_cat(archive, members):
  actual_members = archiver.members(archive)
  not_found = list(set(members)  - set(actual_members))
  if not_found:
    print 'Members not found in %s: %s' % (archive, ', '.join(not_found))
    return 1
  print_member_name = len(members) > 1
  for member in members:
    content = archiver.extract_member_to_string(archive, member)
    if print_member_name:
      print '%s:' % (member)
    print content
  return 0

def _command_help(archive):
  help = TarballUtil.autoconf_help(archive)
  print help
  return 0

def _command_grep(archive, pattern):
  result = TarballUtil.grep(archive, pattern)
  print result
  return 0

def _command_patch_prepare(archive, dest_dir):
  TarballUtil.patch_prepare(archive, dest_dir)
  return 0

def _command_patch_make(working_dir):
  patch = TarballUtil.patch_make(path.abspath(working_dir))
  print patch
  return 0

def _command_extract(archives, dest_dir, base_dir, strip_common_base):
  dest_dir = path.abspath(dest_dir)
  #print "         archives: ", archives
  #print "         dest_dir: ", dest_dir
  #print "         base_dir: ", base_dir
  #print "strip_common_base: ", strip_common_base

  for archive in archives:
    archiver.extract(archive,
                     dest_dir,
                     base_dir = None,
                     strip_common_base = strip_common_base,
                     strip_head = None,
                     include = None,
                     exclude = None)

def _command_create(root_dir, name, version, revision):
  root_dir = path.abspath(root_dir)
  #print "         root_dir: ", root_dir
  #print "             name: ", name
  #print "          version: ", version
  #print "         revision: ", revision

  package_info = package_descriptor(name, version, revision)
  base_dir = package_info.full_name
  filename = '%s.tar.gz' % (base_dir)
  print "         base_dir: ", base_dir
  archiver.create(filename, root_dir, base_dir = base_dir)

def _command_info(filename):
  common_base = archiver.common_base(filename)
  print '   filename: %s' % (filename)
  print 'common_base: %s' % (common_base)
  return 0

def _command_patch(args):
  patches = []
  for patch in args.patches:
    patches.append(path.abspath(patch))

  exit_code, msg = Patch.patch(patches,
                               args.cwd,
                               strip = args.strip,
                               backup = args.backup,
                               posix = args.posix)
  return exit_code

def _command_find(root_dir, name, version):
  tarball = TarballUtil.find(root_dir, name, version)
  if len(tarball) != 1:
    print "Error: too many tarballs found: %s" % (tarball)
    return 1
  print tarball[0]
  return 0

def _command_download(name, url, tag):
  from rebuild.git import Git
  from bes.common import time_util
  import urlparse
  parts = urlparse.urlparse(url)
  site = parts.netloc.split('.')[0]
  timestamp = time_util.timestamp(delimiter = '.', milliseconds = False)
  archive = '%s-%s-%s-%s.tar.gz' % (name, site, tag, timestamp)
  Git.download_tarball(name, tag, url, archive)
  print archive
  return 0

def _command_diff(archive1, archive2):
  diff = TarballUtil.diff(archive1, archive2, strip_common_base = True)
  print diff
  return 0

if __name__ == '__main__':
  raise SystemExit(main())
