#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.system import execute, log, os_env
from bes.fs import file_util
from bes.common import check
from bes.text import string_list
from bes.compat.url_compat import urljoin

from .storage_base import storage_base

from rebuild.base import build_blurb

from .artifactory_requests import artifactory_requests

class storage_artifactory(storage_base):

  _CACHED_AVAILABLE_FILENAME = 'available.json'
  
  def __init__(self, config):
    build_blurb.add_blurb(self, 'rebuild')
    log.add_logging(self, 'storage_artifactory')
    check.check_storage_factory_config(config)
    self._config = config
    self._hostname = config.download_credentials.values['hostname']
    self._remote_root_dir = path.join(config.download_credentials.root_dir, config.repo)
    self._local_root_dir = config.local_cache_dir
    file_util.mkdir(self._local_root_dir)
    self._cached_available_filename = path.join(self._local_root_dir, self._CACHED_AVAILABLE_FILENAME)
    if config.no_network:
      self._available_files = self._load_available_local()
    else:
      self._available_files = self._load_available_remote()
    self._update_filename_map()
    
  def __str__(self):
    return 'artifactory:%s%s' % (self._hostname, self._remote_root_dir)

  def _load_available_remote(self):
    return string_list([ entry.filename for entry in self.list_all_files() ])

  def _load_available_local(self):
    if not path.isfile(self._cached_available_filename):
      self.blurb('artifactory: no cached available files dbindex found at: %s' % (self._cached_available_filename))
      return string_list()
    try:
      self.blurb('artifactory: using cached available files db: %s' % (path.relpath(self._cached_available_filename)))
      return string_list.from_json(self._cached_available_filename)
    except Exception as ex:
      self.blurb('artifactory: ignoring corrupt cached available files db: %s' % (self._cached_available_filename))
      return string_list()

  def _update_filename_map(self):
    self._filename_map = {}
    for file_path in self._available_files:
      filename = path.basename(file_path)
      assert not filename in self._filename_map
      self._filename_map[filename] = file_path
    
  def _download_file(self, filename):
    downloaded_filename = self._downloaded_filename(filename)
    remote_path = self.remote_filename_abs(filename)
    url = self._hostname + remote_path
    self.log_d('_download_file: filename=%s; downloaded_filename=%s; remote_path=%s; url=%s' % (filename, downloaded_filename, remote_path, url))
    artifactory_requests.download_to_file(downloaded_filename, url,
                                          self._config.download_credentials.credentials.username,
                                          self._config.download_credentials.credentials.password)

  def _downloaded_filename(self, filename):
    return path.join(self._local_root_dir, filename)

  #@abstractmethod
  def find_tarball(self, filename):
    file_path = self._filename_map.get(filename, None)
    if not file_path:
      return None
    return self._downloaded_filename(file_path)

  #@abstractmethod
  def ensure_source(self, filename):
    if filename.startswith(self._local_root_dir):
      filename = file_util.remove_head(filename, self._local_root_dir)
    downloaded_filename = self._downloaded_filename(filename)
    if path.exists(downloaded_filename):
      return True
    self.blurb('downloading tarball from %s %s to %s' % (str(self), filename,
                                                         path.relpath(downloaded_filename)))
    self._download_file(filename)
    return path.exists(downloaded_filename)

  #@abstractmethod
  def search(self, name):
    name = name.lower()
    result = []
    for file_path in self._filename_map.values():
      if name in file_path:
        result.append(file_path)
    return result

  #@abstractmethod
  def upload(self, local_filename, remote_filename, local_checksum):
    self.log_d('upload: local_filename=%s; remote_filename=%s; local_checksum=%s' % (local_filename, remote_filename, local_checksum))
    url = self._hostname + remote_filename
    self.log_d('upload: url=%s' % (url))
    download_url = artifactory_requests.upload(url, local_filename,
                                               self._config.upload_credentials.credentials.username,
                                               self._config.upload_credentials.credentials.password)
    self.log_d('upload: download_url=%s' % (download_url))
    verification_checksums = artifactory_requests.fetch_checksums(download_url,
                                                                  self._config.download_credentials.credentials.username,
                                                                  self._config.download_credentials.credentials.password)
    if verification_checksums.sha1 != local_checksum:
      print('Failed to verify checksum.  Something went wrong.  FIXME: should delete the remote file.')
      return False
    return True

  #@abstractmethod
  def remote_checksum(self, remote_filename):
    remote_filename = file_util.lstrip_sep(remote_filename)
    remote_path = self.remote_filename_abs(remote_filename)
    auth = (self._config.download_credentials.credentials.username, self._config.download_credentials.credentials.password)
    #url = urljoin(self._hostname, remote_path)
    url = self._hostname + remote_path
    checksums = artifactory_requests.fetch_checksums(url,
                                                     self._config.download_credentials.credentials.username,
                                                     self._config.download_credentials.credentials.password)
    return checksums.sha1 if checksums else None

  #@abstractmethod
  def remote_filename_abs(self, remote_filename):
    assert not path.isabs(remote_filename)
    return path.join(self._remote_root_dir, remote_filename)

  #@abstractmethod
  def list_all_files(self):
    entries = artifactory_requests.list_all_files(self._hostname,
                                                  self._config.download_credentials.root_dir,
                                                  self._config.repo,
                                                  self._config.download_credentials.credentials.username,
                                                  self._config.download_credentials.credentials.password)
    return [ self._entry(*entry) for entry in entries ]
