#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path, re
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
from .source_finder_db_dict import source_finder_db_dict
from .source_finder_db_pcloud import source_finder_db_pcloud
from .source_finder_db_entry import source_finder_db_entry
from .source_finder_db import source_finder_db
from .source_tool import source_tool

from rebuild.pcloud import pcloud, pcloud_error, pcloud_credentials

class sources_cli(object):

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

    # retire
    retire_parser = subparsers.add_parser('retire', help = 'Retire a tarball in the database.')
    retire_parser.add_argument('what',
                               action = 'store',
                               default = None,
                               type = str,
                               help = 'What to retire.  Can be a filename, checksum or local file name. [ None ]')
    
    # db
    db_parser = subparsers.add_parser('db', help = 'Print the remote db.')
    db_parser.add_argument('-r', '--raw',
                           action = 'store_true',
                           default = False,
                           help = 'Print the raw json data. [ False ]')
    
    # find
    find_parser = subparsers.add_parser('find', help = 'Find a tarball in the database.')
    find_parser.add_argument('what',
                             action = 'store',
                             default = None,
                             type = str,
                             help = 'What to find.  Can be a filename, checksum or local file name. [ None ]')
    
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

    if args.command == 'publish':
      return self._command_publish(args.filename, args.remote_folder, args.dry_run)
    elif args.command == 'sync':
      return self._command_sync(args.local_directory, args.remote_directory)
    elif args.command == 'db':
      return self._command_db(args.raw)
    elif args.command == 'find':
      return self._command_find(args.what)
    elif args.command == 'retire':
      return self._command_retire(args.what)
      
    raise RuntimeError('Invalid command: %s' % (args.command))

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
    remote_checksum = self._checksum_file(filename, remote_folder)
    local_checksum = file_util.checksum('sha1', filename)
    if remote_checksum == local_checksum:
      print('Already exists: %s' % (remote_path))
      return 0
    if dry_run:
      print('Would upload %s => %s' % (filename, remote_path))
      return 0
    
    local_mtime = file_util.mtime(filename)
    print('Uploading %s => %s' % (filename, remote_path))
    self._pcloud.upload_file(filename, path.basename(remote_path), folder_path = path.dirname(remote_path))
    verification_checksum = self._checksum_file(filename, remote_folder)
    if verification_checksum != local_checksum:
      print('Failed to verify checksum.  Something went wrong.')
    db = source_finder_db_pcloud(self._pcloud)
    key = file_util.remove_head(remote_path, self._pcloud_root_dir)
    db.load()
    if key in db:
      print('File alaready in db something is wrong: %s.' % (key))
      return 1
    db[key] = source_finder_db_entry(key, local_mtime, local_checksum)
    db.save()
    return 0

  def _checksum_file(self, filename, remote_folder):
    remote_path = self._remote_path(filename, remote_folder)
    try:
      checksum = self._pcloud.checksum_file(file_path = remote_path)
    except pcloud_error as ex:
      if ex.code == pcloud_error.FILE_NOT_FOUND:
        checksum = None
      else:
        raise ex
    return checksum

  def _sources_db_filename(self):
    return path.join(self._pcloud_root_dir, source_finder_db_dict.DB_FILENAME)
  
  def _command_db(self, raw):
    db = source_finder_db_pcloud(self._pcloud)
    db.load()
    if raw:
      print(db.to_json())
    else:
      db.dump()
    return 0

  def _do_find(self, what):
    db = source_finder_db_pcloud(self._pcloud)
    db.load()
    entry = None
    blurb = ''
    if path.isfile(what):
      blurb = 'checksum'
      what = file_util.checksum('sha1', what)
    if re.match('([a-f0-9A-F]{40})', what):
      blurb = 'checksum'
      entry = db.find_by_checksum(what)
    else:
      blurb = 'file'
      entry = db.get(what, None)
    return ( db, blurb, entry )
  
  def _command_find(self, what):
    db, blurb, entry = self._do_find(what)
    if not entry:
      print('%s not found: %s' % (blurb, what))
      return 1
    print('%s %s %s' % (entry.filename, entry.mtime, entry.checksum))
    return 0
  
  def _command_retire(self, what):
    db, blurb, entry = self._do_find(what)
    if not entry:
      print('%s not found: %s' % (blurb, what))
      return 1
    file_path = self._pcloud.make_path(entry.filename)
    self._pcloud.delete_file(file_path = file_path)
    del db[entry.filename]
    print('Uploading db.')
    db.save()
    return 0
  
  @classmethod
  def run(clazz):
    raise SystemExit(sources_cli().main())
