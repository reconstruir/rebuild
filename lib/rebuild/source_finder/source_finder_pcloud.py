#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path
from bes.fs import file_find
from bes.common import json_util

from .source_finder import source_finder
from .source_finder_db import source_finder_db

from rebuild.pcloud import pcloud

class source_finder_pcloud(source_finder):

  def __init__(self, remote_root_dir, local_root_dir, email, password):
    self.remote_root_dir = remote_root_dir
    self.local_root_dir = local_root_dir
    self.pcloud = pcloud(email, password)
    self.db = self._reload_db()
    print(self.db)
    
  def _reload_db(self):
    try:
      content = self.pcloud.download_to_bytes(file_path = '/sources/sources_db.json')
      return json.loads(content)
    except pcloud_error as ex:
      return {}
    
  #@abstractmethod
  def find_source(self, name, version, system):
    return self._find_by_name_and_version(self.where, name, version, system)

  #@abstractmethod
  def find_tarball(self, filename):
    return self._find_by_filename(self.where, filename)
