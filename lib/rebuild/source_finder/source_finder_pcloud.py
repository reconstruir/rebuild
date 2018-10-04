#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path
from bes.fs import file_find, file_util
from bes.common import check, json_util

from .source_finder import source_finder
from .source_finder_db_file import source_finder_db_file

from rebuild.base import build_blurb
from rebuild.pcloud import pcloud

class source_finder_pcloud(source_finder):

  def __init__(self, remote_root_dir, local_root_dir, credentials, no_network = False):
    build_blurb.add_blurb(self, 'rebuild')
    check.check_pcloud_credentials(credentials)
    self.remote_root_dir = remote_root_dir
    self.local_root_dir = local_root_dir
    self.pcloud = pcloud(credentials)
    del credentials
    self.db = self._load_db()
    self._update_filename_map()
    file_util.mkdir(self.local_root_dir)
    
  def __str__(self):
    return 'pcloud:%s' % (self.remote_root_dir)

  def _load_db(self):
    try:
      remote_db_file_path = path.join(self.remote_root_dir, source_finder_db_file.DB_FILENAME)
      self.blurb('downloading sources db from pcloud:%s' % (remote_db_file_path))
      content = self.pcloud.download_to_bytes(file_path = remote_db_file_path)
      return source_finder_db_file.from_json(content)
    except pcloud_error as ex:
      return source_finder_db_file()

  def _update_filename_map(self):
    self._filename_map = {}
    for file_path, entry in self.db.items():
      filename = path.basename(file_path)
      assert not filename in self._filename_map
      self._filename_map[filename] = entry
    
  def _download_file(self, filename):
    downloaded_filename = self._downloaded_filename(filename)
    file_util.ensure_file_dir(downloaded_filename)
    remote_path = path.join(self.remote_root_dir, filename)
    self.pcloud.download_to_file(downloaded_filename, file_path = remote_path)

  def _downloaded_filename(self, filename):
    return path.join(self.local_root_dir, filename)
    
  #@abstractmethod
  def find_source(self, name, version, system):
    return self._find_by_name_and_version(self.where, name, version, system)

  #@abstractmethod
  def find_tarball(self, filename):
    entry = self._filename_map.get(filename, None)
    if not entry:
      return None
    return self._downloaded_filename(entry.filename)

  #@abstractmethod
  def ensure_source(self, filename):
    if filename.startswith(self.local_root_dir):
      filename = file_util.remove_head(filename, self.local_root_dir)
    downloaded_filename = self._downloaded_filename(filename)
    if path.exists(downloaded_filename):
      return True
    self.blurb('downloading tarball from pcloud:%s to ' % (path.join(self.remote_root_dir, filename),
                                                           path.relpath(downloaded_filename)))
    self._download_file(filename)
    return path.exists(downloaded_filename)
