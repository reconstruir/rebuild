#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs import file_util, temp_file

from bes.common.check import check
from bes.common.json_util import json_util

from .storage_db_base import storage_db_base
from .storage_db_dict import storage_db_dict
from .storage_db_entry import storage_db_entry
from .source_tool import source_tool

class storage_db_file(storage_db_base):

  def __init__(self, root_dir):
    self._root_dir = root_dir
    self.db_filename = path.join(self._root_dir, self.DB_FILENAME)

  #@abstractmethod
  def load(self):
    'Load the db from its source.'
    db = storage_db_dict.from_file(self.db_filename)
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
        db[filename] = storage_db_entry(filename, mtime, file_util.checksum('sha1', filepath))
    # Check for any files that were removed locally
    for entry in db.entries():
      if entry.filename not in current_filenames:
        del db[entry.filename]
    self._db = db

  #@abstractmethod
  def save(self):
    'Save the db from its source.'
    self._db.save_to_file(self.db_filename)

  @classmethod
  def make_temp_db(clazz, db_content, delete = True):
    root = temp_file.make_temp_dir(delete = delete)
    db_filename = path.join(root, clazz.DB_FILENAME)
    file_util.save(db_filename, content = db_content)
    return clazz(root)

#check.register_class(storage_db_file)
