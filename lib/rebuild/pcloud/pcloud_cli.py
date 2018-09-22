#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path
from collections import namedtuple

from bes.common import check
from bes.compat import StringIO
from bes.fs import file_util, file_checksum_list
from bes.text import text_table

from rebuild.source_finder import source_tool

from .pcloud import pcloud
from .pcloud_error import pcloud_error
from .pcloud_metadata import pcloud_metadata

class pcloud_cli(object):

  def __init__(self):
    self._parser = argparse.ArgumentParser(description = 'Tool to interact with pcloud.')
    subparsers = self._parser.add_subparsers(help = 'commands', dest = 'command')

    # ls
    ls_parser = subparsers.add_parser('ls', help = 'List directory.')
    self._add_common_options(ls_parser)
    ls_parser.add_argument('-R', '--recursive',
                           action = 'store_true',
                           default = False,
                           help = 'Recurse into subdirs. [ False ]')
    ls_parser.add_argument('-r', '--reversed',
                           action = 'store_true',
                           default = False,
                           help = 'Reverese the order when sorting.. [ False ]')
    ls_parser.add_argument('-c', '--checksums',
                            action = 'store_true',
                            default = False,
                           help = 'Also fetch file checksums. [ False ]')
    ls_parser.add_argument('-T', '--tree',
                           action = 'store_true',
                           default = False,
                           help = 'Show the results as a tree. [ False ]')
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
    self._add_common_options(checksum_parser)
    checksum_parser.add_argument('filename',
                                 action = 'store',
                                 default = '/',
                                 type = str,
                                 help = 'The folder to list. [ / ]')

    # upload
    upload_parser = subparsers.add_parser('upload', help = 'Upload file.')
    self._add_common_options(upload_parser)
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

    # sync
    sync_parser = subparsers.add_parser('sync', help = 'Sync sources directory to pcloud.')
    self._add_common_options(sync_parser)
    sync_parser.add_argument('local_folder',
                             action = 'store',
                             default = None,
                             type = str,
                             help = 'The local folder to sync from. [ None ]')
    sync_parser.add_argument('remote_folder',
                             action = 'store',
                             default = None,
                             type = str,
                             help = 'The remote folder to sync to. [ None ]')
    
  def main(self):
    args = self._parser.parse_args()
    self._email = args.email
    self._password = args.password

    try:
      if args.command == 'ls':
        return self._command_ls(args.folder, args.recursive, args.reversed, args.tree, args.checksums,
                                args.long_form, args.use_id, args.human_readable)
      elif args.command == 'rm':
        return self._command_rm(args.filename, args.use_id)
      elif args.command == 'mkdir':
        return self._command_mkdir(args.folder, args.parents)
      elif args.command == 'rmdir':
        return self._command_rmdir(args.folder, args.recursive, args.use_id)
      elif args.command == 'chk':
        return self._command_checksum_file(args.filename)
      elif args.command == 'upload':
        return self._command_upload(args.filename, args.folder, args.use_id)
      elif args.command == 'sync':
        return self._command_sync(args.local_folder, args.remote_folder)
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

  def _command_ls(self, folder, recursive, reversed, tree, checksums, long_form, use_id, human_readable):
    pc = pcloud(self._email, self._password)
    if use_id:
      items = pc.list_folder(folder_id = folder, recursive = recursive, checksums = checksums)
    else:
      items = pc.list_folder(folder_path = folder, recursive = recursive, checksums = checksums)
    if tree:
      self._print_items_tree(folder, items, human_readable)
    else:
      self._print_items(items, long_form, human_readable)
    return 0

  def _print_items_tree(self, folder, items, human_readable):
    if not items:
      return
    root = pcloud.items_to_tree(folder, items)
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
  
  def _command_sync(self, local_folder, remote_folder):
    print('sync %s to %s' % (local_folder, remote_folder))
    print('updating local index: %s' % (local_folder))
    source_tool.update_sources_index(local_folder)
    index = file_checksum_list.load_checksums_file(path.join(local_folder, 'sources_index.json'))
    #print(index)
    pc = pcloud(self._email, self._password)
    print('fetching remote file list: %s' % (remote_folder))
    remote_files = pc.list_folder(folder_path = remote_folder, recursive = True, checksums = True)
    print(remote_files)
    return 0

  @classmethod
  def _flatten_items(clazz, items):
    print('sync %s to %s' % (local_folder, remote_folder))
    print('updating local index: %s' % (local_folder))
    source_tool.update_sources_index(local_folder)
    index = file_checksum_list.load_checksums_file(path.join(local_folder, 'sources_index.json'))
    #print(index)
    pc = pcloud(self._email, self._password)
    print('fetching remote file list: %s' % (remote_folder))
    remote_files = pc.list_folder(folder_path = remote_folder, recursive = True, checksums = True)
    print(remote_files)
    return 0
  
  
  @classmethod
  def run(clazz):
    raise SystemExit(pcloud_cli().main())
