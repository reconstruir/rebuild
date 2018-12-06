#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path, re, time
from collections import namedtuple

from bes.system import log
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

class what_resolver(object):
  def __init__(self, what):
    self.checksum = None
    self.filename = None
    if path.isfile(what):
      self.blurb = 'local_checksum'
      self.checksum = file_util.checksum('sha1', what)
    if re.match('([a-f0-9A-F]{40})', what):
      self.blurb = 'checksum'
      self.checksum = what
    else:
      self.blurb = 'filename'
    assert self.blurb

  def __str__(self):
    return str(self.__dict__)
  
class sources_cli(object):

  def __init__(self):
    log.add_logging(self, tag = 'sources_cli')
    self._parser = argparse.ArgumentParser(description = 'Tool to deal with rebuild sources.')
    pcloud_credentials.add_command_line_args(self._parser)
    subparsers = self._parser.add_subparsers(help = 'commands', dest = 'command')

    # publish
    publish_parser = subparsers.add_parser('publish', help = 'Publish a source tarball to cloud.')
    publish_parser.add_argument('local_filename',
                                action = 'store',
                                default = None,
                                type = str,
                                help = 'The tarball to publish to cloud. [ None ]')
    publish_parser.add_argument('--filename',
                                action = 'store',
                                default = None,
                                type = str,
                                help = 'Optional remote filename to use. [ None ]')
    publish_parser.add_argument('--folder',
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
    
    # retire_db
    retire_db_parser = subparsers.add_parser('retire_db', help = 'Retire an entry directly in the database.')
    retire_db_parser.add_argument('what',
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
      return self._command_publish(args.local_filename, args.filename, args.folder, args.dry_run)
    elif args.command == 'sync':
      return self._command_sync(args.local_directory, args.remote_directory)
    elif args.command == 'db':
      return self._command_db(args.raw)
    elif args.command == 'find':
      return self._command_find(args.what)
    elif args.command == 'retire':
      return self._command_retire(args.what)
    elif args.command == 'retire_db':
      return self._command_retire_db(args.what)
      
    raise RuntimeError('Invalid command: %s' % (args.command))

  def _remote_path(self, filename, remote_folder):
    filename = path.basename(filename)
    if remote_folder:
      return path.join(self._pcloud_root_dir, remote_folder, filename)
    else:
      return path.join(self._pcloud_root_dir, filename[0].lower(), filename)
  
  def _command_publish(self, local_filename, remote_filename, remote_folder, dry_run):
    if not path.isfile(local_filename):
      raise IOError('File not found: %s' % (local_filename))
    if path.isabs(remote_folder):
      print('remote path should not be absolute.')
      return 1
    remote_filename = remote_filename or local_filename
    remote_path = self._remote_path(remote_filename, remote_folder)
    self.log_d('_command_publish() remote_filename=%s; remote_path=%s' % (remote_filename, remote_path))
    remote_checksum = self._checksum_file(file_path = remote_path)
    local_checksum = file_util.checksum('sha1', local_filename)
    if remote_checksum == local_checksum:
      print('Already exists: %s' % (remote_path))
      return 0
    if dry_run:
      print('Would upload %s => %s' % (local_filename, remote_path))
      return 0
    
    local_mtime = file_util.mtime(local_filename)
    print('Uploading %s => %s' % (local_filename, remote_path))
    upload_rv = self._pcloud.upload_file(local_filename, path.basename(remote_path),
                                         folder_path = path.dirname(remote_path))
    self.log_d('_command_publish() upload_rv=%s - %s' % (upload_rv, type(upload_rv)))
    file_id = upload_rv[0]['fileid']
    verification_checksum = self._checksum_file_with_retry(file_id = file_id)
    if verification_checksum != local_checksum:
      print('Failed to verify checksum.  Something went wrong.')
      return 1
    db = source_finder_db_pcloud(self._pcloud)
    key = file_util.remove_head(remote_path, self._pcloud_root_dir)
    db.load()
    if key in db:
      print('File alaready in db something is wrong: %s.' % (key))
      return 1
    db[key] = source_finder_db_entry(key, local_mtime, local_checksum)
    db.save()
    print('success')
    return 0

  def _checksum_file(self, file_path = None, file_id = None):
    assert file_path or file_id
    try:
      self.log_d('_checksum_file() trying to checksum filename=%s; file_id=%s' % (file_path, file_id))
      checksum = self._pcloud.checksum_file(file_path = file_path, file_id = file_id)
    except pcloud_error as ex:
      self.log_d('caught exception: %s' % (str(ex)))
      if ex.code in [ pcloud_error.FILE_NOT_FOUND, pcloud_error.PARENT_DIR_MISSING ]:
        checksum = None
      else:
        raise ex
    return checksum

  def _checksum_file_with_retry(self, file_path = None, file_id = None):
    for i in range(0, 4):
      checksum = self._checksum_file(file_path = file_path, file_id = file_id)
      if checksum:
        self.log_d('checksum attempt %d worked for file_path=%s; file_id=%s' % (i, file_path, file_id))
        return checksum
        self.log_d('checksum attempt %d failed for file_path=%s; file_id=%s' % (i, file_path, file_id))
      time.sleep(0.250)
    return False
  
    remote_path = self._remote_path(filename, remote_folder)
    try:
      checksum = self._pcloud.checksum_file(file_path = remote_path)
    except pcloud_error as ex:
      if ex.code in [ pcloud_error.FILE_NOT_FOUND, pcloud_error.PARENT_DIR_MISSING ]:
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

  _found_item = namedtuple('_found_item', 'db, blurb, entry, exact')

  def _do_find(self, what, exact):
    db = source_finder_db_pcloud(self._pcloud)
    db.load()
    entry = None
    blurb = ''
    result = []
    wr = what_resolver(what)
    if wr.checksum:
      entry = db.find_by_checksum(wr.checksum)
      result.append(self._found_item(db, wr.blurb, entry, True))
    else:
      entry = db.get(wr.filename, None)
      if entry:
        result.append(self._found_item(db, wr.blurb, entry, True))
      else:
        if not exact:
          for filename in db.files():
            if what in filename:
              entry = db.get(filename, None)
              assert entry
              result.append(self._found_item(db, wr.blurb, entry, False))
    return result
  
  def _command_find(self, what):
    items = self._do_find(what, False)
    if not items:
      print('\"%s\" not found' % (what))
      return 1
    for item in items:
      exact_blurb = 'exact' if item.exact else 'possible'
      print('%s %-13s %s %s' % (item.entry.filename, item.entry.mtime, item.entry.checksum, exact_blurb))
    return 0
    
  def _command_retire(self, what):
    items = self._do_find(what, True)
    if not items:
      print('\"%s\" not found' % (what))
      return 1
    if len(items) != 1:
      print('\"%s\" matched more than 1 item.  something is screwy' % (what))
      return 1
    item = items[0]
    file_path = self._pcloud.make_path(item.entry.filename)
    self._pcloud.delete_file(file_path = file_path)
    db = source_finder_db_pcloud(self._pcloud)
    db.load()
    del db[item.entry.filename]
    print('Uploading db.')
    db.save()
    return 0
  
  def _command_retire_db(self, what):
    wr = what_resolver(what)

    db = source_finder_db_pcloud(self._pcloud)
    db.load()

    if wr.checksum:
      entry = db.find_by_checksum(wr.checksum)
      if not entry:
        print('checksum not found: %s' % (wr.checksum))
        return 1

    if wr.filename:
      entry = db.get(wr.filename, None)
      if not entry:
        print('file not found: %s' % (wr.checksum))
        return 1

    del db[entry.filename]
    db.save()
    return 0
  
  @classmethod
  def run(clazz):
    raise SystemExit(sources_cli().main())
