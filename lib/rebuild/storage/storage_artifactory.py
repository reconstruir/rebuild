#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.system import execute, log, os_env
from bes.fs import file_util
from bes.common import check
from bes.text import string_list
from bes.compat.url_compat import urljoin

from rebuild.base import build_blurb

from rebuild.artifactory.artifactory_requests import artifactory_requests

from .storage_base import storage_base
from .storage_address import storage_address

class storage_artifactory(storage_base):

  _CACHED_AVAILABLE_FILENAME = 'available.json'
  
  def __init__(self, config):
    build_blurb.add_blurb(self, 'rebuild')
    log.add_logging(self, 'storage_artifactory')
    check.check_storage_factory_config(config)
    check.check_storage_config(config.storage_config)
    self._config = config
    #self._hostname = config.download_credentials.values['hostname']
#    self._remote_root_dir = path.join(config.download_credentials.root_dir, config.repo)
    self._address = self.make_address()
    self._local_root_dir = config.local_cache_dir
    self._no_network = config.no_network
    file_util.mkdir(self._local_root_dir)
    self._cached_available_filename = path.join(self._local_root_dir, self._CACHED_AVAILABLE_FILENAME)
    self.reload_available()
    
  def __str__(self):
    return 'artifactory:%s' % (str(self._address))

  #@abstractmethod
  def reload_available(self):
    if self._no_network:
      self._available_files = self._load_available_local()
    else:
      self._available_files = self._load_available_remote()
  
  def _load_available_remote(self):
    files = string_list(self.list_all_files())
    file_util.save(self._cached_available_filename, content = files.to_json())
    return files

  def _load_available_local(self):
    if not path.isfile(self._cached_available_filename):
      self.blurb('artifactory: no cached available files dbindex found at: %s' % (self._cached_available_filename))
      return string_list()
    try:
      self.blurb('artifactory: using cached available files db: %s' % (path.relpath(self._cached_available_filename)))
      return string_list.from_json(file_util.read(self._cached_available_filename))
    except Exception as ex:
      self.blurb('artifactory: ignoring corrupt cached available files db: %s' % (self._cached_available_filename))
      return string_list()
    
  def _download_file(self, remote_filename):
    downloaded_filename = self._downloaded_filename(remote_filename)
    address = self.make_address(remote_filename)
    self.log_d('_download_file: remote_filename=%s; downloaded_filename=%s; address=%s' % (remote_filename, downloaded_filename, address))
    artifactory_requests.download_to_file(downloaded_filename,
                                          address,
                                          self._config.storage_config.download.username,
                                          self._config.storage_config.download.password)
    
  def _downloaded_filename(self, filename):
    return path.join(self._local_root_dir, filename)

  #@abstractmethod
  def find_tarball(self, filename):
    if not filename in self._available_files:
      return None
    return self._downloaded_filename(filename)

  #@abstractmethod
  def ensure_source(self, filename):
    #assert filename.startswith(self._local_root_dir)
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
    for filename in self._available_files:
      if name in filename:
        result.append(filename)
    return result

  #@abstractmethod
  def upload(self, local_filename, remote_filename, local_checksum):
    self.log_d('upload: local_filename=%s; remote_filename=%s; local_checksum=%s' % (local_filename, remote_filename, local_checksum))
    address = self.make_address(remote_filename)
    self.log_d('upload: address=%s' % (str(address)))
    download_url = artifactory_requests.upload(address, local_filename,
                                               self._config.storage_config.upload.username,
                                               self._config.storage_config.upload.password)
    self.log_d('upload: download_url=%s' % (download_url))
    verification_checksums = artifactory_requests.get_checksums_for_url(download_url,
                                                                        self._config.storage_config.download.username,
                                                                        self._config.storage_config.download.password)
    if verification_checksums.sha256 != local_checksum:
      return False
    return True

  #@abstractmethod
  def set_properties(self, filename, properties):
    address = self.make_address(filename)
    return artifactory_requests.set_properties(address, properties,
                                               self._config.storage_config.upload.username,
                                               self._config.storage_config.upload.password)
  
  #@abstractmethod
  def remote_checksum(self, remote_filename):
    address = self.make_address(remote_filename)
    auth = (self._config.storage_config.download.username, self._config.storage_config.download.password)
    checksums = artifactory_requests.get_checksums(address,
                                                   self._config.storage_config.download.username,
                                                   self._config.storage_config.download.password)
    return checksums.sha256 if checksums else None

  #@abstractmethod
  def list_all_files(self):
    entries = artifactory_requests.list_all_files(self._address,
                                                  self._config.storage_config.download.username,
                                                  self._config.storage_config.download.password)
    return [ entry[0] for entry in entries ]

  def make_address(self, filename = None):
    return storage_address(self._config.storage_config.location,
                           self._config.storage_config.repo,
                           self._config.storage_config.root_dir,
                           self._config.sub_repo,
                           filename)
