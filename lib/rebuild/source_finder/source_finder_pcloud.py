#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path
from bes.fs import file_find, file_util
from bes.common import check, json_util

from .source_finder import source_finder
from .source_finder_db import source_finder_db

from rebuild.pcloud import pcloud

class source_finder_pcloud(source_finder):

  def __init__(self, remote_root_dir, local_root_dir, credentials):
    check.check_pcloud_credentials(credentials)
    self.remote_root_dir = remote_root_dir
    self.local_root_dir = local_root_dir
    self.pcloud = pcloud(credentials)
    del credentials
    self.db = self._reload_db()
    self._download_dir = path.join(self.local_root_dir, 'downloads')
    file_util.mkdir(self._download_dir)
    print(self.db) #.files())
    
  def _reload_db(self):
    print('reloading db')
    try:
      content = self.pcloud.download_to_bytes(file_path = '/sources/sources_db.json')
      return json.loads(content)
    except pcloud_error as ex:
      print('db is empty')
      return {}

  def _download_file(self, filename):
    local_path = path.join(self._download_dir, filename)
    file_util.ensure_file_dir(local_path)
    remote_path = path.join(self.remote_root_dir, filename)
    self.pcloud.download_to_file(local_path, file_path = remote_path)
    
  #@abstractmethod
  def find_source(self, name, version, system):
    return self._find_by_name_and_version(self.where, name, version, system)

  #@abstractmethod
  def find_tarball(self, filename):
    return self._find_by_filename(self.where, filename)
