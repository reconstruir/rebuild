#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path
from bes.fs import file_find, file_util
from bes.common import check, json_util

from .source_finder import source_finder
from .source_finder_db_dict import source_finder_db_dict

from rebuild.base import build_blurb
from rebuild.pcloud import pcloud, pcloud_error

class source_finder_pcloud(source_finder):

  def __init__(self, local_root_dir, credentials, no_network = False):
    check.check_pcloud_credentials(credentials)
    credentials.validate_or_raise(lambda: RuntimeError('Invalid pcloud credentials.'))
    build_blurb.add_blurb(self, 'rebuild')
    check.check_pcloud_credentials(credentials)
    if not credentials.is_valid():
      raise RuntimeError('Invalid pcloud credentials.')
    self.remote_root_dir = credentials.root_dir
    self.local_root_dir = local_root_dir
    self.pcloud = pcloud(credentials)
    del credentials
    self._local_db_file_path = path.join(self.local_root_dir, source_finder_db_dict.DB_FILENAME)
    self._remote_db_file_path = path.join(self.remote_root_dir, source_finder_db_dict.DB_FILENAME)
    if no_network:
      self.db = self._load_db_local()
    else:
      self.db = self._load_db_remote()
    self._update_filename_map()
    file_util.mkdir(self.local_root_dir)
    
  def __str__(self):
    return 'pcloud:%s' % (self.remote_root_dir)

  def _load_db_remote(self):
    try:
      self.blurb('pcloud: using remote db: %s' % (self._remote_db_file_path))
      content = self.pcloud.download_to_bytes(file_path = self._remote_db_file_path)
      sf = source_finder_db_dict.from_json(content)
      file_util.save(path.join(self.local_root_dir, source_finder_db_dict.DB_FILENAME), content = content)
      return sf
    except pcloud_error as ex:
      return source_finder_db_dict()

  def _load_db_local(self):
    if not path.isfile(self._local_db_file_path):
      self.blurb('pcloud: not local db found at: %s' % (self._local_db_file_path))
      return source_finder_db_dict()
    try:
      self.blurb('pcloud: using local db: %s' % (path.relpath(self._local_db_file_path)))
      content = file_util.read(self._local_db_file_path)
      return source_finder_db_dict.from_json(content)
    except Exception as ex:
      self.blurb('pcloud: local db is corrupt: %s' % (self._local_db_file_path))
      return source_finder_db_dict()

  def _update_filename_map(self):
    self._filename_map = {}
    for file_path, entry in self.db.dict_items():
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
    self.blurb('downloading tarball from pcloud:%s to %s' % (path.join(self.remote_root_dir, filename),
                                                             path.relpath(downloaded_filename)))
    self._download_file(filename)
    return path.exists(downloaded_filename)

  #@abstractmethod
  def search(self, name):
    result = []
    for file_path, entry in self.db.dict_items():
      if name.lower() in entry.filename.lower():
        result.append(path.basename(entry.filename))
    return result
