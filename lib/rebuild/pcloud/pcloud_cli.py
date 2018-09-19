#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path
from collections import namedtuple

from bes.common import check
from bes.text import text_table, text_cell_renderer
from bes.compat import StringIO

from rebuild.pcloud import pcloud

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
    ls_parser.add_argument('folder',
                           action = 'store',
                           default = '/',
                           type = str,
                           help = 'The folder to list. [ / ]')
    
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
    if args.command == 'ls':
      return self._command_list_folder(args.folder, args.recursive, args.checksums, args.long_form)
    elif args.command == 'chk':
      return self._command_checksum_file(args.filename)
    raise RuntimeError('Invalid command: %s' % (args.command))

  def _add_common_options(self, parser):
    parser.add_argument('-e', '--email',
                        action = 'store',
                        default = os.environ.get('PCLOUD_EMAIL', None),
                        type = str,
                        help = 'The pcloud account password. [ None ]')
    parser.add_argument('-p', '--password',
                        action = 'store',
                        default = os.environ.get('PCLOUD_PASSWORD', None),
                        type = str,
                        help = 'The pcloud account password. [ None ]')

  class list_item_short(namedtuple('list_item_short', 'name, is_folder')):
    
    def __new__(clazz, item):
      check.check_metadata(item)
      name = item.name
      is_folder = item.is_folder
      return clazz.__bases__[0].__new__(clazz, name, is_folder)

    def __str__(self):
      buf = StringIO()
      buf.write(self.name)
      if self.is_folder:
        buf.write('/')
      return buf.getvalue()
    
  class list_item_long(namedtuple('list_item_long', 'size, name')):
    
    def __new__(clazz, item):
      check.check_metadata(item)
      if item.is_folder:
        name = '%s/' % (item.name)
      else:
        name = item.name
      size = item.size
      return clazz.__bases__[0].__new__(clazz, size, name)

  def _command_list_folder(self, folder, recursive, checksums, long_form):
    pc = pcloud(self._email, self._password)
    items = pc.list_folder(folder, recursive = True, checksums = True)
    if not items:
      return 0
    if long_form:
      items = [ self.list_item_long(item) for item in items ]
      table = text_table(data = items)
      print(table)
    else:
      items = [ self.list_item_short(item) for item in items ]
      print(' '.join([ str(item) for item in items ]))
    return 0
  
  def _command_checksum_file(self, filename):
    return 0
  
  @classmethod
  def run(clazz):
    raise SystemExit(pcloud_cli().main())
