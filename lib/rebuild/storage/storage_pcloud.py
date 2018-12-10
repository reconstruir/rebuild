#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_util
from bes.common import check
from bes.text import string_list

from .storage_base import storage_base

from rebuild.base import build_blurb
from rebuild.pcloud import pcloud, pcloud_error, pcloud_credentials

class storage_pcloud(storage_base):

  _CACHED_AVAILABLE_FILENAME = 'available.json'
  
  def __init__(self, config):
    check.check_storage_factory_config(config)
    build_blurb.add_blurb(self, 'rebuild')
    self._remote_root_dir = config.download_credentials.root_dir
    self._local_root_dir = config.local_cache_dir
    file_util.mkdir(self._local_root_dir)
    pcloud_cred = pcloud_credentials(config.download_credentials.credentials.username,
                                     config.download_credentials.credentials.password)
    self.pcloud = pcloud(pcloud_cred, self._remote_root_dir)
    self._cached_available_filename = path.join(self._local_root_dir, self._CACHED_AVAILABLE_FILENAME)
    if config.no_network:
      self._available_files = self._load_available_local()
    else:
      self._available_files = self._load_available_remote()
    self._update_filename_map()
    
  def __str__(self):
    return 'pcloud:%s' % (self._remote_root_dir)

  def _load_available_remote(self):
    try:
      files = self.pcloud.quick_list_folder(self._remote_root_dir, recursive = True, relative = True)
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

  def _update_filename_map(self):
    self._filename_map = {}
    for file_path in self._available_files:
      filename = path.basename(file_path)
      assert not filename in self._filename_map
      self._filename_map[filename] = file_path
    
  def _download_file(self, filename):
    downloaded_filename = self._downloaded_filename(filename)
    file_util.ensure_file_dir(downloaded_filename)
    remote_path = path.join(self._remote_root_dir, filename)
    self.pcloud.download_to_file(downloaded_filename, file_path = remote_path)

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
    self.blurb('downloading tarball from pcloud:%s to %s' % (path.join(self._remote_root_dir, filename),
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
