#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path, re, time
from collections import namedtuple

from bes.system import log
from bes.archive import archiver
from bes.common import check, node
from bes.compat import StringIO
from bes.fs import file_find, file_util, temp_file
from bes.common import node
from bes.text import text_table
from bes.url import url_util

from bes.archive import archiver, archive_extension
from rebuild.binary_format import binary_detector
from rebuild.source_ingester import ingest_util

from rebuild.config import storage_config_manager

from .storage_db_entry import storage_db_entry
from .storage_db_dict import storage_db_dict
from .storage_db_entry import storage_db_entry
from .storage_db import storage_db
from .storage_factory import storage_factory

from rebuild.base import build_target
from rebuild.package import artifact_manager_local

from _rebuild_testing.artifact_manager_helper import artifact_manager_helper


# This is a hack to deal with the fact that storage_artifactory is a plugin
# but there is no system (yet) to load such plugins
from rebuild.storage.storage_artifactory import storage_artifactory
from rebuild.storage.storage_local import storage_local

#from rebuild.artifactory.artifactory_requests import artifactory_requests
from rebuild.storage.storage_address import storage_address

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
    ingest_parser.add_argument('--checksum',
                               action = 'store',
                               default = None,
                               type = str,
                               help = 'The checksum for the remote content (url). [ None ]')
    ingest_parser.add_argument('--debug',
                               action = 'store_true',
                               default = False,
                               help = 'Debug mode.  Do not remove temporary files and dirs. [ False ]')
    ingest_parser.add_argument('--repo',
                               action = 'store',
                               default = 'sources',
                               help = 'Repo to ingest to. [ sources ]')

    # update_properties
    update_properties_parser = subparsers.add_parser('update_properties', help = 'Publish artifacts to remote storage.')
    update_properties_parser.add_argument('config',
                                          action = 'store',
                                          default = None,
                                          type = str,
                                          help = 'Config file for storage credentials and providers. [ None ]')
    update_properties_parser.add_argument('provider',
                                          action = 'store',
                                          default = None,
                                          type = str,
                                          help = 'Which provider to use for the upload. [ None ]')
    update_properties_parser.add_argument('local_dir',
                                          action = 'store',
                                          default = None,
                                          type = str,
                                          help = 'Local directory where to look for artifacts to publish. [ None ]')
    update_properties_parser.add_argument('--dry-run',
                                          action = 'store_true',
                                          default = False,
                                          help = 'Do not do any work.  Just print what would happen. [ False ]')

    # publish_artifacts
    publish_artifacts_parser = subparsers.add_parser('publish_artifacts', help = 'Publish artifacts to remote storage.')
    publish_artifacts_parser.add_argument('config_file',
                                          action = 'store',
                                          default = None,
                                          type = str,
                                          help = 'Config file for storage credentials and providers. [ None ]')
    publish_artifacts_parser.add_argument('config_name',
                                          action = 'store',
                                          default = None,
                                          type = str,
                                          help = 'Which config name in config file to use for for the upload. [ None ]')
    publish_artifacts_parser.add_argument('local_dir',
                                          action = 'store',
                                          default = None,
                                          type = str,
                                          help = 'Local directory where to look for artifacts to publish. [ None ]')
    publish_artifacts_parser.add_argument('--dry-run',
                                          action = 'store_true',
                                          default = False,
                                          help = 'Do not do any work.  Just print what would happen. [ False ]')
    publish_artifacts_parser.add_argument('--limit',
                                          action = 'store',
                                          default = None,
                                          type = int,
                                          help = 'Limit the number of artifacts uploaded. [ None ]')
    
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

    # checksum
    checksum_parser = subparsers.add_parser('checksum', help = 'Checksum a local file or url.')
    checksum_parser.add_argument('what',
                                 action = 'store',
                                 default = None,
                                 type = str,
                                 help = 'What to checksum.  Can be local or url. [ None ]')
    
  def main(self):
    args = self._parser.parse_args()
#    credentials = pcloud_credentials.resolve_command_line(args)
#    credentials.validate_or_bail()
#    self._pcloud = pcloud(credentials)
#    self._pcloud_root_dir = credentials.root_dir
#    del credentials

    if args.command == 'ingest':
      return self._command_ingest(args.config, args.provider, args.what, args.remote_filename, args.dry_run,
                                  args.debug, args.arcname, args.checksum, args.repo)
    elif args.command == 'update_properties':
      return self._command_update_properties(args.config, args.provider, args.local_dir, args.dry_run)
    elif args.command == 'publish_artifacts':
      return self._command_publish_artifacts(args.config_file, args.config_name, args.local_dir, args.dry_run, args.limit)
    elif args.command == 'sync':
      return self._command_sync(args.local_directory, args.remote_directory)
    elif args.command == 'files':
      return self._command_files(args.config, args.provider, args.repo)
    elif args.command == 'find':
      return self._command_find(args.what)
    elif args.command == 'retire':
      return self._command_retire(args.what)
    elif args.command == 'checksum':
      return self._command_checksum(args.what)
      
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
  def _make_storage(clazz, command, config_filename, config_name, sub_repo):
    if not path.isfile(config_filename):
      raise IOError('%s: config_filename not found: %s' % (command, config_filename))
    scm = storage_config_manager.from_file(config_filename)
    config = scm.get(config_name)
    if not config:
      raise RuntimeError('%s: \"%s\" not found in %s' % (command, config_name, config_filename))
    local_cache_dir = path.join(os.getcwd(), 'cache', config.provider)
    factory_config = storage_factory.config(local_cache_dir, sub_repo, False, config)
    return storage_factory.create(factory_config)
  
  def _command_ingest(self, config_filename, provider, what, remote_filename,
                      dry_run, debug, arcname, checksum, repo):
    check.check_string(config_filename)
    check.check_string(provider)
    check.check_string(what)
    check.check_string(remote_filename)
    check.check_string(repo)
    if arcname:
      check.check_string(arcname)
    if checksum:
      check.check_string(checksum)
    self.log_d('ingest: config_filename=%s; provider=%s; what=%s; remote_filename=%s; arcname=%s; checksum=%s; repo=%s' % (config_filename,
                                                                                                                           provider,
                                                                                                                           what,
                                                                                                                           remote_filename,
                                                                                                                           arcname,
                                                                                                                           checksum,
                                                                                                                           repo))
    storage = self._make_storage('ingest', config_filename, provider, repo)
    if what.startswith('http'):
      rv = ingest_util.ingest_url(what, remote_filename, arcname, checksum, storage, dry_run = dry_run, debug = debug)
    else:
      rv = ingest_util.ingest_file(what, remote_filename, arcname, storage, dry_run = dry_run, debug = debug)
    print(rv.reason)
    return 0 if rv.success else 1

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

  def _command_update_properties(self, config_filename, provider, local_dir, dry_run):
    check.check_string(config_filename)
    check.check_string(provider)
    check.check_string(local_dir)
    self.log_d('update_properties: config_filename=%s; provider=%s; local_dir=%s; dry_run=%s' % (config_filename,
                                                                                                 provider,
                                                                                                 local_dir,
                                                                                                 dry_run))
    storage = self._make_storage('update_properties', config_filename, provider, 'artifacts')

    if not path.isdir(local_dir):
      raise RuntimeError('not a directory: %s' % (local_dir))

    address = storage.make_address()
    username = storage._config.upload_credentials.credentials.username
    password = storage._config.upload_credentials.credentials.password
    
    am = artifact_manager_local(local_dir)
    bt = build_target.make_host_build_target()
    artifacts = am.list_all_by_descriptor(bt)
    for adesc in artifacts:
      md = am.find_by_artifact_descriptor(adesc, True)
      properties = self._metadata_to_artifactory_properties(md)
      artifact_address = address.mutate_filename(md.filename)
      if dry_run:
        print('would update propertieson %s: %s' % (artifact_address, properties))
      else:
        rv = artifactory_requests.set_properties(artifact_address, properties, username, password)
        if rv:
          print('success: %s' % (md.filename))
        else:
          print(' failed: %s' % (md.filename))
    return 0

  def _command_publish_artifacts(self, config_filename, config_name, local_dir, dry_run, limit):
    check.check_string(config_filename)
    check.check_string(config_name)
    check.check_string(local_dir)
    self.log_d('publish_artifacts: config_filename=%s; config_name=%s; local_dir=%s; dry_run=%s; limit=%s' % (config_filename,
                                                                                                           config_name,
                                                                                                           local_dir,
                                                                                                           dry_run,
                                                                                                           limit))
    if not path.isdir(local_dir):
      raise RuntimeError('not a directory: %s' % (local_dir))

    storage = self._make_storage('publish_artifacts', config_filename, config_name, 'artifacts')

    username = storage._config.storage_config.upload.username
    password = storage._config.storage_config.upload.password

    am = artifact_manager_helper.make_local_artifact_manager(local_dir)
        
    bt = build_target.make_host_build_target(level = 'release', version_minor = '')
    artifacts = am.list_all_by_descriptor(bt)
    # Never publish artifacts with .9999 in their version as that is testing stuff
    artifacts = [ artifact for artifact in artifacts if '.9999' not in artifact.version ]
    if limit:
      artifacts = artifacts[0:limit]
    for adesc in artifacts:
      md = am.find_by_artifact_descriptor(adesc, True)
      md_abs = am.find_by_artifact_descriptor(adesc, False)

      local_filename = md_abs.filename
      remote_filename = md.filename

      self.log_d('publish_artifacts: local_filename=%s; remote_filename=%s' % (local_filename, remote_filename))

      if not path.isfile(local_filename):
        #print('%25s: %s' % ('missing', md.filename))
        continue
      
      remote_checksum = storage.remote_checksum(remote_filename)
      local_checksum = file_util.checksum('sha256', local_filename)

      self.log_d('publish_artifacts: local_checksum=%s; remote_checksum=%s' % (local_checksum, remote_checksum))
      
      if remote_checksum == local_checksum:
        #print('%25s: %s' % ('exists same checksum', md.filename))
        continue
      if remote_checksum is not None and remote_checksum != local_checksum:
        #print('%25s: %s' % ('exists diff checksum', md.filename))
        continue
      if dry_run:
        print('%25s: %s to %s' % ('dry run: would upload', md.filename, storage.make_address(remote_filename)))
      else:
        self.log_d('publish_artifacts: calling upload(%s, %s)' % (md_abs.filename, remote_filename))
        print('%25s: %s' % ('uploading', md.filename))
        upload_rv = storage.upload(local_filename, remote_filename, local_checksum)
        if not upload_rv:
          print('%25s: %s' % ('failed', md.filename))
          return 1
        else:
          print('%25s: %s' % ('uploaded', md.filename))
          properties = self._metadata_to_artifactory_properties(md)
          properties_rv = storage.set_properties(remote_filename, properties)
          if properties_rv:
            print('%25s: %s' % ('set properties', md.filename))
          else:
            print('%25s: %s' % ('failed to set properties', md.filename))
    return 0

  @classmethod
  def _metadata_to_artifactory_properties(clazz, md):
    check.check_package_metadata(md)
    properties = {
      'rebuild.format_version': str(md.format_version),
      'rebuild.name': md.name,
      'rebuild.version': md.version,
      'rebuild.revision': str(md.revision),
      'rebuild.epoch': str(md.epoch),
      'rebuild.system': md.system,
      'rebuild.level': md.level,
      'rebuild.arch': md.arch,
      'rebuild.distro': md.distro,
      'rebuild.distro_version_major': md.distro_version_major,
      'rebuild.distro_version_minor': md.distro_version_minor,
      'rebuild.requirements': md.requirements.to_string_list(),
      }
    return properties

  def _command_checksum(self, what):
    check.check_string(what)
    self.log_d('checksum: what=%s' % (what))
    if what.startswith('http'):
      local_filename = url_util.download_to_temp_file(what)
    else:
      local_filename = what
    checksum = file_util.checksum('sha256', local_filename)
    print(checksum)
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

  
  @classmethod
  def run(clazz):
    raise SystemExit(sources_cli().main())
