#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.system import log
from bes.fs import file_util
from bes.common import check
from bes.text import string_list

from .storage_base import storage_base
from .file_mapping import file_mapping

from rebuild.base import build_blurb
from rebuild.pcloud import pcloud, pcloud_error, pcloud_credentials

class storage_pcloud(storage_base):

  _CACHED_AVAILABLE_FILENAME = 'available.json'
  
  def __init__(self, config):
    build_blurb.add_blurb(self, 'rebuild')
    log.add_logging(self, 'storage_pcloud')
    check.check_storage_factory_config(config)

    self._file_mapping = file_mapping(config.local_cache_dir, path.join(config.download_credentials.root_dir, config.repo), None)
    
    self._remote_root_dir = path.join(config.download_credentials.root_dir, config.repo)
    self._local_root_dir = config.local_cache_dir
    file_util.mkdir(self._local_root_dir)
    pcloud_cred = pcloud_credentials(config.download_credentials.credentials.username,
                                     config.download_credentials.credentials.password)
    self._pcloud = pcloud(pcloud_cred, self._remote_root_dir)
    self._cached_available_filename = path.join(self._local_root_dir, self._CACHED_AVAILABLE_FILENAME)
    if config.no_network:
      self._available_files = self._load_available_local()
    else:
      self._available_files = self._load_available_remote()
    
  def __str__(self):
    return 'pcloud:%s' % (self._remote_root_dir)

  def _load_available_remote(self):
    try:
      files = self._pcloud.quick_list_folder(self._remote_root_dir, recursive = True, relative = True)
      file_util.save(self._cached_available_filename, content = files.to_json())
      return files
    except pcloud_error as ex:
      self.blurb('pcloud: failed to fetch available files from: %s' % (self._remote_root_dir))
      return string_list()

  def _load_available_local(self):
    if not path.isfile(self._cached_available_filename):
      self.blurb('pcloud: no cached available files dbindex found at: %s' % (self._cached_available_filename))
      return string_list()
    try:
      self.blurb('pcloud: using cached available files db: %s' % (path.relpath(self._cached_available_filename)))
      return string_list.from_json(self._cached_available_filename)
    except Exception as ex:
      self.blurb('pcloud: ignoring corrupt cached available files db: %s' % (self._cached_available_filename))
      return string_list()
    
  def _download_file(self, filename):
    downloaded_filename = self._downloaded_filename(filename)
    file_util.ensure_file_dir(downloaded_filename)
    remote_path = path.join(self._remote_root_dir, filename)
    self._pcloud.download_to_file(downloaded_filename, file_path = remote_path)

  def _downloaded_filename(self, filename):
    return path.join(self._local_root_dir, filename)

  #@abstractmethod
  def find_tarball(self, filename):
    if not filename in self._available_files:
      return None
    return self._downloaded_filename(filename)

  #@abstractmethod
  def ensure_source(self, filename):
    if filename.startswith(self._local_root_dir):
      filename = file_util.remove_head(filename, self._local_root_dir)
    downloaded_filename = self._downloaded_filename(filename)
    if path.exists(downloaded_filename):
      return True
    self.blurb('downloading tarball from pcloud:%s to %s' % (path.join(self._remote_root_dir, filename),
                                                             path.relpath(downloaded_filename)))
    self._download_file(filename)
    return path.exists(downloaded_filename)

  #@abstractmethod
  def search(self, name):
    name = name.lower()
    result = []
    for filename in self._available_files:
      if name in filename:
        result.append(filename)
    return result

  #@abstractmethod
  def upload(self, local_filename, remote_filename, local_checksum):
    print('Uploading %s => %s' % (local_filename, remote_filename))
    upload_rv = self._pcloud.upload_file(local_filename, path.basename(remote_filename),
                                         folder_path = path.dirname(remote_filename))
    self.log_d('_command_ingest() upload_rv=%s - %s' % (upload_rv, type(upload_rv)))
    file_id = upload_rv[0]['fileid']
    verification_checksum = self._checksum_file(file_id = file_id)
    if verification_checksum != local_checksum:
      print('Failed to verify checksum.  Something went wrong.  FIXME: should delete the remote file.')
      return False
    return True

  def _checksum_file(self, file_path = None, file_id = None):
    return self._pcloud.checksum_file_safe(file_path = file_path, file_id = file_id)

  #@abstractmethod
  def remote_checksum(self, remote_filename):
    return self._checksum_file(file_path = self.remote_filename_abs(remote_filename))

  #@abstractmethod
  def remote_filename_abs(self, remote_filename):
    assert not path.isabs(remote_filename)
    return path.join(self._remote_root_dir, remote_filename)

  #@abstractmethod
  def list_all_files(self):
    files = self._pcloud.quick_list_folder(self._remote_root_dir, recursive = True, relative = True)
    return [ self._entry(filename, '') for filename in files ]
