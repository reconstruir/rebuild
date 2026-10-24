#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import contextlib
import os.path as path
import sqlite3

from bes.system.check import check
from bes.files.bf_file_ops import bf_file_ops

class storage_local_properties(object):
  '''
  The properties of files in a local storage, kept in a sqlite database at the
  storage root, by filename relative to that root.  They used to be xattrs on
  each file; xattrs are no longer written (rmt/claude-docs/metadata-db-support.md
  Phase 9), and a database also survives copies that drop them.

  Each call opens the database and closes it again, so nothing stays open
  between calls and several processes can share one storage.
  '''

  FILENAME = '.rebuild_properties.db'

  _SCHEMA = '''
CREATE TABLE IF NOT EXISTS properties(
  filename TEXT NOT NULL,
  key TEXT NOT NULL,
  value TEXT NOT NULL,
  PRIMARY KEY (filename, key)
);
'''

  def __init__(self, root_dir):
    check.check_string(root_dir)

    self._db_filename = path.join(root_dir, self.FILENAME)

  @property
  def db_filename(self):
    return self._db_filename

  def set_properties(self, filename, properties):
    'Set each key of properties on filename; a value of None removes the key.'
    check.check_string(filename)
    check.check_dict(properties)

    for key, value in properties.items():
      check.check_string(key)
      check.check_string(value, allow_none = True)
    with self._connect() as db:
      for key, value in properties.items():
        if value is None:
          db.execute('DELETE FROM properties WHERE filename = ? AND key = ?', ( filename, key ))
        else:
          db.execute('INSERT OR REPLACE INTO properties(filename, key, value) VALUES (?, ?, ?)',
                     ( filename, key, value ))

  def get_properties(self, filename):
    'The properties of filename, as a dict; {} if it has none.'
    check.check_string(filename)

    if not path.isfile(self._db_filename):
      return {}
    with self._connect() as db:
      rows = db.execute('SELECT key, value FROM properties WHERE filename = ? ORDER BY key',
                        ( filename, )).fetchall()
    return { key: value for key, value in rows }

  @contextlib.contextmanager
  def _connect(self):
    bf_file_ops.ensure_file_dir(self._db_filename)
    connection = sqlite3.connect(self._db_filename)
    try:
      with connection:
        connection.execute(self._SCHEMA)
        yield connection
    finally:
      connection.close()
