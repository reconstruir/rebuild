#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path
from collections import namedtuple

from bes.common import check
from bes.compat import StringIO
from bes.fs import file_util
from bes.text import text_table

from .pcloud import pcloud
from .pcloud_error import pcloud_error

class pcloud_cli(object):

  def __init__(self):
    self._parser = argparse.ArgumentParser(description = 'Tool to interact with pcloud.')
    subparsers = self._parser.add_subparsers(help = 'commands', dest = 'command')

    # ls
    ls_parser = subparsers.add_parser('ls', help = 'List directory.')
    self._add_common_options(ls_parser)
    ls_parser.add_argument('-r', '--recursive',
                           action = 'store_true',
                           default = False,
                           help = 'Recurse into subdirs. [ False ]')
    ls_parser.add_argument('-c', '--checksums',
                           action = 'store_true',
                           default = False,
                           help = 'Also fetch file checksums. [ False ]')
    ls_parser.add_argument('-l', '--long-form',
                           action = 'store_true',
                           default = False,
                           help = 'Long form. [ False ]')
    ls_parser.add_argument('-H', '--human-readable',
                           action = 'store_true',
                           default = False,
                           help = 'Print human readable sizes. [ False ]')
    ls_parser.add_argument('-i', '--use-id',
                           action = 'store_true',
                           default = False,
                           help = 'Use pcloud id instead of path. [ False ]')
    ls_parser.add_argument('folder',
                           action = 'store',
                           default = '/',
                           type = str,
                           help = 'The folder to list. [ / ]')

    # rm
    rm_parser = subparsers.add_parser('rm', help = 'Remove file.')
    self._add_common_options(rm_parser)
    rm_parser.add_argument('-i', '--use-id',
                           action = 'store_true',
                           default = False,
                           help = 'Use pcloud id instead of path. [ False ]')
    rm_parser.add_argument('filename',
                           action = 'store',
                           default = None,
                           type = str,
                           help = 'The file to delete. [ None ]')
    
    # mkdir
    mkdir_parser = subparsers.add_parser('mkdir', help = 'Make directory.')
    self._add_common_options(mkdir_parser)
    mkdir_parser.add_argument('-p', '--parents',
                              action = 'store_true',
                              default = False,
                              help = 'no error if existing, make parent directories as needed. [ False ]')
    mkdir_parser.add_argument('folder',
                              action = 'store',
                              default = None,
                              type = str,
                              help = 'The folder to make. [ None ]')
    
    # rmdir
    rmdir_parser = subparsers.add_parser('rmdir', help = 'Make directory.')
    self._add_common_options(rmdir_parser)
    rmdir_parser.add_argument('folder',
                              action = 'store',
                              default = None,
                              type = str,
                              help = 'The folder to remove. [ None ]')
    
    
    # checksum
    checksum_parser = subparsers.add_parser('chk', help = 'Checksum file.')
    self._add_common_options(checksum_parser)
    checksum_parser.add_argument('filename',
                                 action = 'store',
                                 default = '/',
                                 type = str,
                                 help = 'The folder to list. [ / ]')
    
###    # Bulbs
###    bulbs_parser = subparsers.add_parser('bulbs', help = 'List bulbs.')
###    self._add_common_options(bulbs_parser)
###
###
###    command_group = self.parser.add_mutually_exclusive_group()
###    command_group.add_argument('--list-all', action = 'store_true')
###    command_group.add_argument('--modversion', nargs = '+', action = 'store',
###                               help = 'Print the version for the given modules.')
###    command_group.add_argument('--cflags', nargs = '+', action = 'store',
###                               help = 'Print the cflags for the given modules.')
###    command_group.add_argument('--print-requires', nargs = '+', action = 'store',
###                               help = 'Print the requires property for the given modules.')
###    self.pc = caca_pkg_config(self.PKG_CONFIG_PATH.path)
    
  def main(self):
    args = self._parser.parse_args()
    self._email = args.email
    self._password = args.password

    try:
      if args.command == 'ls':
        return self._command_ls(args.folder, args.recursive, args.checksums,
                                args.long_form, args.use_id, args.human_readable)
      elif args.command == 'rm':
        return self._command_rm(args.filename, args.use_id)
      elif args.command == 'mkdir':
        return self._command_mkdir(args.folder, args.parents)
      elif args.command == 'rmdir':
        return self._command_rmdir(args.folder)
      elif args.command == 'chk':
        return self._command_checksum_file(args.filename)
    except pcloud_error as ex:
      print(str(ex))
      raise SystemExit(1)
      
    raise RuntimeError('Invalid command: %s' % (args.command))

  def _add_common_options(self, parser):
    parser.add_argument('-E', '--email',
                        action = 'store',
                        default = os.environ.get('PCLOUD_EMAIL', None),
                        type = str,
                        help = 'The pcloud account password. [ None ]')
    parser.add_argument('-P', '--password',
                        action = 'store',
                        default = os.environ.get('PCLOUD_PASSWORD', None),
                        type = str,
                        help = 'The pcloud account password. [ None ]')

  class list_item_short(namedtuple('list_item_short', 'name, is_folder')):
    
    def __new__(clazz, item):
      check.check_pcloud_metadata(item)
      name = item.name
      is_folder = item.is_folder
      return clazz.__bases__[0].__new__(clazz, name, is_folder)

    def __str__(self):
      buf = StringIO()
      buf.write(self.name)
      if self.is_folder:
        buf.write('/')
      return buf.getvalue()
    
  class list_item_long(namedtuple('list_item_long', 'size, name, pcloud_id, content_type, checksum')):
    
    def __new__(clazz, item, human_readable):
      check.check_pcloud_metadata(item)
      if item.is_folder:
        name = '%s/' % (item.name)
        content_type = 'folder'
      else:
        name = item.name
        content_type = item.content_type
      if item.size:
        if human_readable:
          size = file_util.sizeof_fmt(item.size)
        else:
          size = item.size
      else:
        size = ''
      return clazz.__bases__[0].__new__(clazz, size, name, item.pcloud_id, content_type, item.checksum)

  def _command_ls(self, folder, recursive, checksums, long_form, use_id, human_readable):
    pc = pcloud(self._email, self._password)
    if use_id:
      items = pc.list_folder(folder_id = folder, recursive = recursive, checksums = checksums)
    else:
      items = pc.list_folder(folder_path = folder, recursive = recursive, checksums = checksums)
    if not items:
      return 0
    if long_form:
      items = [ self.list_item_long(item, human_readable) for item in items ]
      table = text_table(data = items, column_delimiter = '  ')
      table.set_labels(tuple([ x.upper() for x in items[0]._fields ]))
      print(table)
    else:
      items = [ self.list_item_short(item) for item in items ]
      print(' '.join([ str(item) for item in items ]))
    return 0

  def _command_rm(self, filename, use_id):
    pc = pcloud(self._email, self._password)
    if use_id:
      items = pc.delete_file(file_id = filename)
    else:
      items = pc.delete_file(file_path = filename)
    return 0
  
  def _command_mkdir(self, folder, parents):
    pc = pcloud(self._email, self._password)
    rv = pc.create_folder(folder_path = folder)
    return 0
  
  def _command_rmdir(self, folder):
    pc = pcloud(self._email, self._password)
    rv = pc.delete_folder(folder_path = folder)
    return 0
  
  def _command_checksum_file(self, filename):
    pc = pcloud(self._email, self._password)
    chk = pc.checksum_file(file_path = filename)
    print(chk)
    return 0
  
  @classmethod
  def run(clazz):
    raise SystemExit(pcloud_cli().main())
