#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common.check import check
from bes.fs.file_util import file_util

class storage_db_entry(namedtuple('storage_db_entry', 'filename, mtime, checksum')):
  
  def __new__(clazz, filename, mtime, checksum):
    return clazz.__bases__[0].__new__(clazz, filename, mtime, checksum)

  @classmethod
  def from_file(clazz, filename, directory = None):
    if directory:
      file_path = path.join(directory, filename)
    else:
      file_path = filename
    mtime = file_util.mtime(file_path)
    checksum = file_util.checksum('sha1', file_path)
    return clazz(filename, mtime, checksum)

  @classmethod
  def from_list(clazz, l):
    check.check_list(l)
    filename = l[0]
    mtime = l[1]
    checksum = l[2]
    return clazz(filename, mtime, checksum)

  def to_list(self):
    return list(self)

check.register_class(storage_db_entry)
