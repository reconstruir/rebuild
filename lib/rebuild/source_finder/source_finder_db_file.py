#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs import file_util, temp_file

from bes.common import check, json_util

from .source_finder_db_base import source_finder_db_base
from .source_finder_db_dict import source_finder_db_dict
from .source_finder_db_entry import source_finder_db_entry
from .source_tool import source_tool

class source_finder_db_file(source_finder_db_base):

  def __init__(self, root_dir):
    self._root_dir = root_dir
    self.db_filename = path.join(self._root_dir, self.DB_FILENAME)

  #@abstractmethod
  def load(self):
    'Load the db from its source.'
    db = source_finder_db_dict.from_file(self.db_filename)
    current_filenames = source_tool.find_sources(self._root_dir)
    # Check for new or modified files
    for filename in current_filenames:
      filepath = path.join(self._root_dir, filename)
      mtime = file_util.mtime(filepath)
      add_entry = False
      if filename in db:
        # If filename is already in db, then check if the mtime change.  If so, redo the checksum
        entry = db[filename]
        add_entry = db[filename].mtime != mtime
      else:
        add_entry = True
      if add_entry:
        db[filename] = source_finder_db_entry(filename, mtime, file_util.checksum('sha1', filepath))
    # Check for any files that were removed locally
    for entry in db.entries():
      if entry.filename not in current_filenames:
        del db[entry.filename]
    self._db = db

  #@abstractmethod
  def save(self):
    'Save the db from its source.'
    self._db.save_to_file(self.db_filename)

  def _make_db(self, sources):
    db = source_finder_db_dict()
    for f in sources:
      p = path.join(self._root_dir, f)
      mtime = file_util.mtime(p)
      checksum = self._read_checksum(f)
      db[f] = source_finder_db_entry(f, mtime, checksum)
    return db
      
  def _read_checksum(self, filename):
    p = path.join(self._root_dir, filename)
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
    return self._db.files()

  def items(self):
    return self._db.items()

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

check.register_class(source_finder_db_file)

