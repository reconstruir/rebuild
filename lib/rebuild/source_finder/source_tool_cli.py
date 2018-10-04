#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path
from collections import namedtuple

from bes.archive import archiver
from bes.common import check, node
from bes.compat import StringIO
from bes.fs import file_checksum_list, file_find, file_util
from bes.common import node
from bes.text import text_table

#from .pcloud import pcloud
#from .pcloud_metadata import pcloud_metadata

from .tarball_finder import tarball_finder
from .source_finder_db_entry import source_finder_db_entry
from .source_tool import source_tool

from rebuild.pcloud import pcloud, pcloud_error, pcloud_credentials

class source_tool_cli(object):

  def __init__(self):
    self._parser = argparse.ArgumentParser(description = 'Tool to deal with rebuild sources.')
    pcloud_credentials.add_command_line_args(self._parser)
    subparsers = self._parser.add_subparsers(help = 'commands', dest = 'command')

    # publish
    publish_parser = subparsers.add_parser('publish', help = 'Publish a source tarball to cloud.')
    publish_parser.add_argument('filename',
                                action = 'store',
                                default = None,
                                type = str,
                                help = 'The tarball to publish to cloud. [ None ]')
    publish_parser.add_argument('remote_folder',
                                action = 'store',
                                default = None,
                                type = str,
                                nargs = '?',
                                help = 'Optional remote folder to publish to. [ None ]')
    publish_parser.add_argument('--dry-run',
                                action = 'store_true',
                                default = False,
                                help = 'Do not do any work.  Just print what would happen. [ False ]')
    
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
    
  def main(self):
    args = self._parser.parse_args()
    credentials = pcloud_credentials.resolve_command_line(args)
    credentials.validate_or_bail()
    self._pcloud = pcloud(credentials)
    self._pcloud_root_dir = credentials.root_dir
    del credentials

    if args.command == 'find':
      return self._command_find(args.directory)
    elif args.command == 'publish':
      return self._command_publish(args.filename, args.remote_folder, args.dry_run)
    elif args.command == 'sync':
      return self._command_sync(args.local_directory, args.remote_directory)
      
    raise RuntimeError('Invalid command: %s' % (args.command))

  def _command_find(self, directory):
    source_tool.update_sources_index(directory)
    return 0

  def _remote_path(self, filename, remote_folder):
    filename = path.basename(filename)
    if remote_folder:
      return path.join(self._pcloud_root_dir, remote_folder, filename)
    else:
      return path.join(self._pcloud_root_dir, filename[0].lower(), filename)
  
  def _command_publish(self, filename, remote_folder, dry_run):
    if not path.isfile(filename):
      raise IOError('File not found: %s' % (filename))
    remote_path = self._remote_path(filename, remote_folder)
    try:
      remote_checksum = self._pcloud.checksum_file(file_path = remote_path)
    except pcloud_error as ex:
      if ex.code == pcloud_error.FILE_NOT_FOUND:
        remote_checksum = None
      else:
        raise ex
    local_checksum = file_util.checksum('sha1', filename)
    if remote_checksum == local_checksum:
      print('Already exists: %s' % (remote_path))
      return 0
    if dry_run:
      print('Would upload %s => %s' % (filename, remote_path))
    else:
      print('Uploading %s => %s' % (filename, remote_path))
      self._pcloud.upload_file(filename, path.basename(remote_path), folder_path = path.dirname(remote_path))
    return 0
  
  @classmethod
  def run(clazz):
    raise SystemExit(source_tool_cli().main())
