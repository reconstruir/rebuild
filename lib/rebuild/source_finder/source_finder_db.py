#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs import file_util, temp_file

from bes.common import check, json_util

from .source_finder_db_file import source_finder_db_file
from .source_finder_db_entry import source_finder_db_entry
from .source_tool import source_tool

class source_finder_db(object):

  DB_FILENAME = 'sources_db.json'
  
  def __init__(self, root):
    self._root = root
    self.db_filename = path.join(self._root, self.DB_FILENAME)
    self._db = source_finder_db_file()
    self._update_db()

  def _update_db(self):
    self._db = source_finder_db_file.from_file(self.db_filename)
    current_sources = source_tool.find_sources(self._root)
    self._db = self._make_db(current_sources)
    self._db.save_to_file(self.db_filename)

  def _make_db(self, sources):
    db = source_finder_db_file()
    for f in sources:
      p = path.join(self._root, f)
      mtime = file_util.mtime(p)
      checksum = self._read_checksum(f)
      db[f] = source_finder_db_entry(f, mtime, checksum)
    return db
      
  def _read_checksum(self, filename):
    p = path.join(self._root, filename)
    mtime = file_util.mtime(p)
    item = self._db.get(filename, None)
    if item:
      if mtime == item[1]:
        assert item[2]
        return item[2]
    return file_util.checksum('sha1', p)

  def checksum(self, filename):
    return self._db.checksum(filename)

  def files(self):
    return self._db.files(filename)

  def checksum_dict(self):
    return self._db.checksum_dict()
  
  def delta(self, other):
    check.check_source_finder_dbe(other)
    return self._db.delta(other._db)

  @classmethod
  def make_temp_db(clazz, db_content, delete = True):
    root = temp_file.make_temp_dir(delete = delete)
    db_filename = path.join(root, clazz.DB_FILENAME)
    file_util.save(db_filename, content = db_content)
    return clazz(root)

check.register_class(source_finder_db)

