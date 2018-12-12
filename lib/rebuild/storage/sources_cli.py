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

from rebuild.config import storage_config

from .tarball_finder import tarball_finder
from .storage_db_entry import storage_db_entry
from .storage_db_dict import storage_db_dict
from .storage_db_entry import storage_db_entry
from .storage_db import storage_db
from .storage_factory import storage_factory

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
    subparsers = self._parser.add_subparsers(help = 'commands', dest = 'command')

    # ingest
    ingest_parser = subparsers.add_parser('ingest', help = 'Ingest a local or remote tarball or executable to pcloud.')
    ingest_parser.add_argument('config',
                                action = 'store',
                                default = None,
                                type = str,
                                help = 'Config file for storage credentials and providers. [ None ]')
    ingest_parser.add_argument('provider',
                                action = 'store',
                                default = None,
                                type = str,
                                help = 'Which provider to use for the upload. [ None ]')
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
    ingest_parser.add_argument('--debug',
                               action = 'store_true',
                               default = False,
                               help = 'Debug mode.  Do not remove temporary files and dirs. [ False ]')
    ingest_parser.add_argument('--repo',
                               action = 'store',
                               default = 'sources',
                               help = 'Repo to ingest to. [ sources ]')

    # publish_artifacts
    publish_artifacts_parser = subparsers.add_parser('publish_artifacts', help = 'Publish artifacts to remote storage.')
    publish_artifacts_parser.add_argument('config',
                                          action = 'store',
                                          default = None,
                                          type = str,
                                          help = 'Config file for storage credentials and providers. [ None ]')
    publish_artifacts_parser.add_argument('provider',
                                          action = 'store',
                                          default = None,
                                          type = str,
                                          help = 'Which provider to use for the upload. [ None ]')
    publish_artifacts_parser.add_argument('local_dir',
                                          action = 'store',
                                          default = None,
                                          type = str,
                                          help = 'Local directory where to look for artifacts to publish. [ None ]')
    publish_artifacts_parser.add_argument('--dry-run',
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
    
    # files
    files_parser = subparsers.add_parser('files', help = 'Print all available sources.')
    files_parser.add_argument('config',
                              action = 'store',
                              default = None,
                              type = str,
                              help = 'Config file for storage credentials and providers. [ None ]')
    files_parser.add_argument('provider',
                              action = 'store',
                              default = None,
                              type = str,
                              help = 'Which provider to use for the upload. [ None ]')
    files_parser.add_argument('--repo',
                              action = 'store',
                              default = 'sources',
                              help = 'Repo to list files for. [ sources ]')
    
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
#    credentials = pcloud_credentials.resolve_command_line(args)
#    credentials.validate_or_bail()
#    self._pcloud = pcloud(credentials)
#    self._pcloud_root_dir = credentials.root_dir
#    del credentials

    if args.command == 'ingest':
      return self._command_ingest(args.config, args.provider, args.what, args.remote_filename, args.dry_run,
                                  args.debug, args.arcname, args.repo)
    elif args.command == 'publish_artifacts':
      return self._command_publish_artifacts(args.config, args.provider, args.local_dir, args.dry_run)
    elif args.command == 'sync':
      return self._command_sync(args.local_directory, args.remote_directory)
    elif args.command == 'files':
      return self._command_files(args.config, args.provider, args.repo)
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
  
  def _remote_filename(self, remote_filename):
    return path.join(self._pcloud_root_dir, remote_filename)

  @classmethod
  def _make_storage(clazz, command, config_filename, provider, repo):
    if not path.isfile(config_filename):
      raise IOError('%s: config_filename not found: %s' % (command, config_filename))
    config = storage_config.from_file(config_filename)
    storage_cache_dir = path.join(os.getcwd(), 'cache', provider)
    download_credentials = config.get('download', provider)
    upload_credentials = config.get('upload', provider)
    local_storage_dir = path.join(storage_cache_dir, provider)
    factory_config = storage_factory.config(local_storage_dir,  repo, False, download_credentials, upload_credentials)
    return storage_factory.create(provider, factory_config)
  
  def _command_ingest(self, config_filename, provider, what, remote_filename,
                      dry_run, debug, arcname, repo):
    check.check_string(config_filename)
    check.check_string(provider)
    check.check_string(what)
    check.check_string(remote_filename)
    check.check_string(repo)
    self.log_d('ingest: config_filename=%s; provider=%s; what=%s; remote_filename=%s; arcname=%s; repo=%s' % (config_filename,
                                                                                                              provider,
                                                                                                              what,
                                                                                                              remote_filename,
                                                                                                              arcname,
                                                                                                              repo))
    storage = self._make_storage('ingest', config_filename, provider, repo)

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
    def _cleanup_tmp_files():
      if not debug:
        file_util.remove(tmp_files_to_cleanup)

    # if local_filename is an executable, archive into a tarball first
    if is_exe:
      local_filename = ingest_util.fix_executable(local_filename, debug = debug)
      self.log_d('_command_ingest: fixed executable: %s' % (local_filename))
      tmp_files_to_cleanup.append(local_filename)
      self.log_d('_command_ingest: calling archive_binary(%s, %s, %s)' % (local_filename, remote_basename, arcname))
      local_filename = ingest_util.archive_binary(local_filename, remote_basename, arcname, debug = debug)
      self.log_d('_command_ingest: calling archive_binary() returns %s' % (local_filename))
      tmp_files_to_cleanup.append(local_filename)

    remote_path = storage.remote_filename_abs(remote_filename)
    remote_checksum = storage.remote_checksum(remote_filename)
    local_checksum = file_util.checksum('sha1', local_filename)
    self.log_d('_command_ingest: remote_path=%s; remote_checksum=%s; local_checksum=%s' % (remote_path, remote_checksum, local_checksum))
    if remote_checksum == local_checksum:
      _cleanup_tmp_files()
      print('a file with checksum %s already exists: %s' % (local_checksum, remote_path))
      return 0
    if remote_checksum is not None and remote_checksum != local_checksum:
      _cleanup_tmp_files()
      print('trying to re-ingest a with a different checksum.')
      print(' local_filename: %s' % (local_filename))
      print(' local_checksum: %s' % (local_checksum))
      print('remote_checksum: %s' % (remote_checksum))
      return 1
    if dry_run:
      print('Would upload %s => %s' % (local_filename, remote_path))
      return 0
    
    print('Uploading %s => %s' % (local_filename, remote_path))
    try:
      self.log_d('_command_ingest() calling upload(%s, %s)' % (local_filename, remote_path))
      rv = storage.upload(local_filename, remote_path, local_checksum)
      self.log_d('_command_ingest() rv=%s - %s' % (rv, type(rv)))
      if not rv:
        print('Failed to upload.  Something went wrong.  FIXME: should delete the remote file.')
        return 1
    finally:
      _cleanup_tmp_files()
      
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
  
  def _command_files(self, config_filename, provider, repo):
    check.check_string(config_filename)
    check.check_string(provider)
    self.log_d('files: config_filename=%s; provider=%s' % (config_filename, provider))
    storage = self._make_storage('files', config_filename, provider, repo)
    files = storage.list_all_files()
    tt = text_table(data = files)
    print(str(tt))
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

  def _command_publish_artifacts(self, config_filename, provider, local_dir, dry_run):
    check.check_string(config_filename)
    check.check_string(provider)
    check.check_string(local_dir)
    self.log_d('publish_artifacts: config_filename=%s; provider=%s; local_dir=%s; dry_run=%s' % (config_filename,
                                                                                                 provider,
                                                                                                 local_dir,
                                                                                                 dry_run))
    storage = self._make_storage('ingest', config_filename, provider, 'artifacts')

    if not path.isdir(local_dir):
      raise RuntimeError('not a directory: %s' % (local_dir))

    db_files = file_find.find_fnmatch(local_dir, [ '*.db' ], relative = True, min_depth = 1, max_depth = 1, file_type = file_find.FILE)
    print('db_diles: %s' % (db_files))
    return 0

  
  @classmethod
  def run(clazz):
    raise SystemExit(sources_cli().main())
