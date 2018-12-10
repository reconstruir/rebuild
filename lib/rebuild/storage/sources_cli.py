#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path, re, time
from collections import namedtuple

from bes.system import log
from bes.archive import archiver
from bes.common import check, node
from bes.compat import StringIO
from bes.fs import file_checksum_list, file_find, file_util, temp_file
from bes.common import node
from bes.text import text_table
from bes.url import url_util

from bes.archive import archiver, archive_extension
from rebuild.binary_format import binary_detector
from rebuild.source_ingester import ingest_util


#from .pcloud import pcloud
#from .pcloud_metadata import pcloud_metadata

from .tarball_finder import tarball_finder
from .storage_db_entry import storage_db_entry
from .storage_db_dict import storage_db_dict
from .storage_db_pcloud import storage_db_pcloud
from .storage_db_entry import storage_db_entry
from .storage_db import storage_db
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

    # ingest
    ingest_parser = subparsers.add_parser('ingest', help = 'Ingest a local or remote tarball or executable to pcloud.')
    ingest_parser.add_argument('what',
                                action = 'store',
                                default = None,
                                type = str,
                                help = 'What to ingest.  Can be a tarball or executable.  Can be local file path or remote url. [ None ]')
    ingest_parser.add_argument('remote_filename',
                                action = 'store',
                                default = None,
                                type = str,
                                help = 'Optional remote filename to use. [ None ]')
    ingest_parser.add_argument('--dry-run',
                                action = 'store_true',
                                default = False,
                                help = 'Do not do any work.  Just print what would happen. [ False ]')
    ingest_parser.add_argument('--arcname',
                               action = 'store',
                               default = None,
                               type = str,
                               help = 'The file path for an executable inside an archive if needed. [ None ]')
    
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

    if args.command == 'ingest':
      return self._command_ingest(args.what, args.remote_filename, args.dry_run, args.arcname)
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
  
  def _remote_filename(self, remote_filename):
    return path.join(self._pcloud_root_dir, remote_filename)
  
  def _command_ingest(self, what, remote_filename, dry_run, arcname):
    check.check_string(what)
    check.check_string(remote_filename)
    self.log_d('_command_ingest: what=%s; remote_filename=%s; arcname=%s' % (what, remote_filename, arcname))
    remote_basename = path.basename(remote_filename)
    # If it is a url, download it to a temporary file and use that
    if what.startswith('http'):
      local_filename = url_util.download_to_temp_file(what, basename = 'tmp_download_for_ingest')
      self.log_d('_command_ingest: using remote url %s => %s' % (what, local_filename))
    else:
      self.log_d('_command_ingest: using local file %s' % (what))
      local_filename = what
    if not path.isfile(local_filename):
      raise IOError('local_filename not found: %s' % (local_filename))
    is_valid_archive = archiver.is_valid(local_filename)
    is_exe = binary_detector.is_executable(local_filename)
    self.log_d('_command_ingest: is_valid_archive=%s; is_exe=%s' % (is_valid_archive, is_exe))
    if not (is_valid_archive or is_exe):
      raise RuntimeError('local_filename should be an archive or executable: %s' % (local_filename))
    tmp_files_to_cleanup = []
    # if local_filename is an executable, archive into a tarball first
    if is_exe:
      # if the executable does not have the right mode, make a tmp copy and fix it
      fixed_mode_local_filename = ingest_util.fix_executable_mode(local_filename)
      self.log_d('_command_ingest: fixed_mode_local_filename=%s' % (fixed_mode_local_filename))
      if fixed_mode_local_filename:
        tmp_files_to_cleanup.append(fixed_mode_local_filename)
        local_filename = fixed_mode_local_filename
      self.log_d('_command_ingest: calling archive_binary(%s, %s, %s)' % (local_filename, remote_basename, arcname))
      local_filename = ingest_util.archive_binary(local_filename, remote_basename, arcname)
      self.log_d('_command_ingest: calling archive_binary() returns %s' % (local_filename))
      tmp_files_to_cleanup.append(local_filename)

    remote_path = self._remote_filename(remote_filename)
    remote_checksum = self._checksum_file(file_path = remote_path)
    local_checksum = file_util.checksum('sha1', local_filename)
    self.log_d('_command_ingest: remote_path=%s; remote_checksum=%s; local_checksum=%s' % (remote_path, remote_checksum, local_checksum))
    if remote_checksum == local_checksum:
      file_util.remove(tmp_files_to_cleanup)
      print('Already exists: %s' % (remote_path))
      return 0
    if remote_checksum is not None and remote_checksum != local_checksum:
      file_util.remove(tmp_files_to_cleanup)
      raise RuntimeError('trying to re-ingest a file with a different checksum: %s => %s' % (local_filename, remote_path))
    if dry_run:
      print('Would upload %s => %s' % (local_filename, remote_path))
      return 0
    
    local_mtime = file_util.mtime(local_filename)
    print('Uploading %s => %s' % (local_filename, remote_path))
    try:
      upload_rv = self._pcloud.upload_file(local_filename, path.basename(remote_path),
                                           folder_path = path.dirname(remote_path))
      self.log_d('_command_ingest() upload_rv=%s - %s' % (upload_rv, type(upload_rv)))
      file_id = upload_rv[0]['fileid']
      verification_checksum = self._checksum_file_with_retry(file_id = file_id)
      if verification_checksum != local_checksum:
        print('Failed to verify checksum.  Something went wrong.  FIXME: should delete the remote file.')
        return 1
    finally:
      file_util.remove(tmp_files_to_cleanup)
      
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
    return path.join(self._pcloud_root_dir, storage_db_dict.DB_FILENAME)
  
  def _command_db(self, raw):
    db = storage_db_pcloud(self._pcloud)
    db.load()
    if raw:
      print(db.to_json())
    else:
      db.dump()
    return 0

  _found_item = namedtuple('_found_item', 'db, blurb, entry, exact')

  def _do_find(self, what, exact):
    db = storage_db_pcloud(self._pcloud)
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
    db = storage_db_pcloud(self._pcloud)
    db.load()
    del db[item.entry.filename]
    print('Uploading db.')
    db.save()
    return 0
  
  def _command_retire_db(self, what):
    wr = what_resolver(what)

    db = storage_db_pcloud(self._pcloud)
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
