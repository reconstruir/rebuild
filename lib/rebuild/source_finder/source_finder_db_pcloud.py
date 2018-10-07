#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.common import check
from bes.fs import file_util, temp_file

from .source_finder_db_base import source_finder_db_base
from .source_finder_db_dict import source_finder_db_dict

class source_finder_db_pcloud(source_finder_db_base):

  def __init__(self, pcloud):
#    check.check_pcloud(pcloud)
    self._root_dir = pcloud.root_dir
    self._pcloud = pcloud
    self._remote_db_path = path.join(self._root_dir, self.DB_FILENAME)

  #@abstractmethod
  def load(self):
    'Load the db from its source.'
    db_json = self._pcloud.download_to_bytes(file_path = self._remote_db_path)
    self._dict_db = source_finder_db_dict.from_json(db_json)
    self._db = self._dict_db._db

  #@abstractmethod
  def save(self):
    'Save the db from its source.'
    db_json = self._dict_db.to_json()
    tmp_dir = temp_file.make_temp_dir()
    tmp_db_filename = path.join(tmp_dir, self.DB_FILENAME)
    file_util.save(tmp_db_filename, content = db_json)
    self._pcloud.upload_file(tmp_db_filename,
                             path.basename(self._remote_db_path),
                             folder_path = path.dirname(self._remote_db_path))
