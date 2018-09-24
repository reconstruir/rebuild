#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path
from collections import namedtuple

from bes.common import check
from bes.compat import StringIO
from bes.fs import file_util, file_checksum_list
from bes.text import text_table

from rebuild.source_finder import source_tool
from rebuild.source_finder.source_finder_db import source_finder_db

from .pcloud import pcloud
from .pcloud_error import pcloud_error
from .pcloud_metadata import pcloud_metadata
from .pcloud_credentials import pcloud_credentials

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
                           help = 'Reverese the order when sorting. [ False ]')
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
    checksum_parser.add_argument('-i', '--use-id',
                                 action = 'store_true',
                                 default = False,
                                 help = 'Use pcloud id instead of path. [ False ]')
    checksum_parser.add_argument('filename',
                                 action = 'store',
                                 default = '/',
                                 type = str,
                                 help = 'The folder to list. [ / ]')

    # download
    download_parser = subparsers.add_parser('download', help = 'Download file.')
    self._add_common_options(download_parser)
    download_parser.add_argument('-i', '--use-id',
                                 action = 'store_true',
                                 default = False,
                                 help = 'Use pcloud id instead of path. [ False ]')
    download_parser.add_argument('filename',
                                 action = 'store',
                                 default = '/',
                                 type = str,
                                 help = 'The folder to list. [ / ]')
    download_parser.add_argument('dest_filename',
                                 action = 'store',
                                 default = None,
                                 type = str,
                                 help = 'The detination filenamt. [ / ]')

    # cat
    cat_parser = subparsers.add_parser('cat', help = 'Cat file.')
    self._add_common_options(cat_parser)
    cat_parser.add_argument('-i', '--use-id',
                            action = 'store_true',
                            default = False,
                            help = 'Use pcloud id instead of path. [ False ]')
    cat_parser.add_argument('filename',
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

    if args.email or args.password:
      credentials = pcloud_credentials.from_command_line_args(args.email, args.password)
      del args.email
      del args.password
    else:
      credentials = pcloud_credentials.from_environment()

    if not credentials.is_valid():
      print('No pcloud email or password given.  Set PCLOUD_EMAIL/PCLOUD_PASSWORD or use the --email/--password flag')
      raise SystemExit(1)
      
    self._pcloud = pcloud(credentials)
    del credentials
      
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
        return self._command_checksum_file(args.filename, args.use_id)
      elif args.command == 'download':
        return self._command_download(args.filename, args.dest_filename, args.use_id)
      elif args.command == 'cat':
        return self._command_cat(args.filename, args.use_id)
      elif args.command == 'upload':
        return self._command_upload(args.filename, args.folder, args.use_id)
      elif args.command == 'sync':
        return self._command_sync(args.local_folder, args.remote_folder)
    except pcloud_error as ex:
      print(str(ex))
      raise SystemExit(1)
      
    raise RuntimeError('Invalid command: %s' % (args.command))

  def _add_common_options(self, parser):
    pcloud_credentials.add_command_line_args(parser)

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
    if use_id:
      items = self._pcloud.list_folder(folder_id = folder, recursive = recursive, checksums = checksums)
    else:
      items = self._pcloud.list_folder(folder_path = folder, recursive = recursive, checksums = checksums)
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
    if use_id:
      items = self._pcloud.delete_file(file_id = filename)
    else:
      items = self._pcloud.delete_file(file_path = filename)
    return 0
  
  def _command_mkdir(self, folder, parents):
    rv = self._pcloud.create_folder(folder_path = folder)
    return 0
  
  def _command_rmdir(self, folder, recursive, use_id):
    if use_id:
      rv = self._pcloud.delete_folder(folder_id = folder, recursive = recursive)
    else:
      rv = self._pcloud.delete_folder(folder_path = folder, recursive = recursive)
    return 0
  
  def _command_checksum_file(self, filename, use_id):
    if use_id:
      checksum = self._pcloud.checksum_file(file_id = filename)
    else:
      checksum = self._pcloud.checksum_file(ile_path = filename)
    print(checksum)
    return 0

  def _command_download(self, filename, dest_filename, use_id):
    if use_id:
      self._pcloud.download_to_file(dest_filename, file_id = filename)
    else:
      self._pcloud.download_to_file(dest_filename, file_path = filename)
    return 0

  def _command_cat(self, filename, use_id):
    if use_id:
      data = self._pcloud.download_to_bytes(file_id = filename)
    else:
      data = self._pcloud.download_to_bytes(file_path = filename)
    print(data)
    return 0

  def _command_upload(self, filename, folder, use_id):
    if use_id:
      self._pcloud.upload_file(filename, path.basename(filename), folder_id = folder)
    else:
      self._pcloud.upload_file(filename, path.basename(filename), folder_path = folder)
    return 0

  def _command_sync(self, local_folder, remote_folder):
    print('sync %s to %s' % (local_folder, remote_folder))
    print('reading local db: %s' % (local_folder))
    db = source_finder_db(local_folder)
    #source_tool.update_sources_index(local_folder)
    #local_checksums = file_checksum_list.load_checksums_file(path.join(local_folder, 'sources_index.json'))
    local_dict = db.checksum_dict()
#    for k, v in local_dict.items():
#      print(' LOCAL: %s %s' % (k, v))
    remote_db_path = path.join(remote_folder, source_finder_db.DB_FILENAME)
    
    print('fetching remote db: %s' % (remote_folder))

    print('fetching remote files: %s' % (remote_folder))
    remote_items = self._pcloud.list_folder(folder_path = remote_folder, recursive = True, checksums = True)
    print('done fetching remote files: %s' % (remote_folder))
    remote_dict = self._items_to_dict(remote_folder, remote_items)
#    for k, v in remote_dict.items():
#      print('REMOTE: %s %s' % (k, v))
    local_set = set(local_dict.items())
    remote_set = set(remote_dict.items())
    not_in_remote = local_set - remote_set
    not_in_local = remote_set - local_set
    for k, v in sorted(dict(not_in_remote).items()):
      local_path = path.join(local_folder, k)
      remote_path = path.join(remote_folder, k)
      #print('NOT IN REMOTE: %s %s' % (k, v))
      print('Uploading: %s' % (remote_path))
      self._pcloud.upload_file(local_path, path.basename(local_path), folder_path = path.dirname(remote_path))
    print('Uploading db file: %s' % (db.db_filename))
    self._pcloud.upload_file(db.db_filename, path.basename(db.db_filename), folder_path = remote_folder)
    return 0
  
  @classmethod
  def _items_to_dict(clazz, folder, items):
    tree = pcloud.items_to_tree(folder, items)
    paths = tree.flat_paths()
    result = {}
    for next_path in paths:
      ps = '/'.join([ x.name for x in next_path.path ])
      ps = file_util.remove_head(ps, folder)
      result[ps] = next_path.node.data.checksum
    return result
  
  @classmethod
  def run(clazz):
    raise SystemExit(pcloud_cli().main())
