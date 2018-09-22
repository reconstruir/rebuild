#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path
from collections import namedtuple

from bes.archive import archiver
from bes.common import check, node
from bes.compat import StringIO
from bes.fs import file_checksum_list, file_find, file_util
from bes.text import text_table

#from .pcloud import pcloud
#from .pcloud_error import pcloud_error
#from .pcloud_metadata import pcloud_metadata

from .tarball_finder import tarball_finder
from .source_item import source_item
from .source_tool import source_tool

class source_tool_cli(object):

  def __init__(self):
    self._parser = argparse.ArgumentParser(description = 'Tool to deal with rebuild sources.')
    subparsers = self._parser.add_subparsers(help = 'commands', dest = 'command')

    # find
    find_parser = subparsers.add_parser('find', help = 'Find source in a directory.')
    find_parser.add_argument('directory',
                             action = 'store',
                             default = None,
                             type = str,
                             help = 'The folder to find source in. [ None ]')
    
    # sync
    sync_parser = subparsers.add_parser('sync', help = 'Remove file.')
    sync_parser.add_argument('-i', '--use-id',
                           action = 'store_true',
                           default = False,
                           help = 'Use pcloud id instead of path. [ False ]')
    sync_parser.add_argument('filename',
                           action = 'store',
                           default = None,
                           type = str,
                           help = 'The file to delete. [ None ]')
    
    # mkdir
    mkdir_parser = subparsers.add_parser('mkdir', help = 'Make directory.')
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
    rmdir_parser.add_argument('-r', '--recursive',
                              action = 'store_true',
                              default = False,
                              help = 'Recurse into subdirs. [ False ]')
    rmdir_parser.add_argument('-i', '--use-id',
                              action = 'store_true',
                              default = False,
                              help = 'Use pcloud id instead of path. [ False ]')
    rmdir_parser.add_argument('folder',
                              action = 'store',
                              default = None,
                              type = str,
                              help = 'The folder to remove. [ None ]')
    
    
    # checksum
    checksum_parser = subparsers.add_parser('chk', help = 'Checksum file.')
    checksum_parser.add_argument('filename',
                                 action = 'store',
                                 default = '/',
                                 type = str,
                                 help = 'The folder to list. [ / ]')

    # upload
    upload_parser = subparsers.add_parser('upload', help = 'Upload file.')
    upload_parser.add_argument('-i', '--use-id',
                               action = 'store_true',
                               default = False,
                               help = 'Use pcloud id instead of path. [ False ]')
    upload_parser.add_argument('filename',
                               action = 'store',
                               default = None,
                               type = str,
                               help = 'The file to upload. [ None ]')
    upload_parser.add_argument('folder',
                               action = 'store',
                               default = None,
                               type = str,
                               help = 'The destination folder or folder_id. [ None ]')

    
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
#    self._email = args.email
#    self._password = args.password

    if args.command == 'find':
      return self._command_find(args.directory)
    elif args.command == 'sync':
      return self._command_sync(args.local_directory, args.remote_directory)
      
    raise RuntimeError('Invalid command: %s' % (args.command))

  def _command_find(self, directory):
    source_tool.update_sources_index(directory)
    return 0

  def _make_item_node(self, item):
    if item.is_folder:
      if item.name != '/':
        name = '%s/' % (item.name)
      else:
        name = '/'
    else:
      name = item.name
    n = node(name)
    for child in item.contents or []:
      child_node = self._make_item_node(child)
      n.children.append(child_node)
    return n
  
  def _print_items_tree(self, folder, items, human_readable):
    if not items:
      return
    root = self._make_item_node(pcloud_metadata(folder, 0, True, 0, None, 'dir', '0', items, 0))
    print(root.to_string(indent = 2))

  def _print_items(self, items, long_form, human_readable):
    if not items:
      return
    if long_form:
      data = [ self.list_item_long(item, human_readable) for item in items ]
      table = text_table(data = data, column_delimiter = '  ')
      table.set_labels( ( 'SIZE', 'NAME', 'PCLOUD ID', 'CONTENT TYPE', 'CHECKSUM' ) )
      print(table)
    else:
      data = [ self.list_item_short(item) for item in items ]
      print(' '.join([ str(item) for item in data ]))
    for item in items:
      if item.contents:
        print('\n%s:' % (item.name))
        self._print_items(item.contents, long_form, human_readable)
  
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
  
  def _command_rmdir(self, folder, recursive, use_id):
    pc = pcloud(self._email, self._password)
    if use_id:
      rv = pc.delete_folder(folder_id = folder, recursive = recursive)
    else:
      rv = pc.delete_folder(folder_path = folder, recursive = recursive)
    return 0
  
  def _command_checksum_file(self, filename):
    pc = pcloud(self._email, self._password)
    chk = pc.checksum_file(file_path = filename)
    print(chk)
    return 0

  def _command_upload(self, filename, folder, use_id):
    pc = pcloud(self._email, self._password)
    if use_id:
      pc.upload_file(filename, path.basename(filename), folder_id = folder)
    else:
      pc.upload_file(filename, path.basename(filename), folder_path = folder)
    return 0
  
  @classmethod
  def run(clazz):
    raise SystemExit(source_tool_cli().main())
