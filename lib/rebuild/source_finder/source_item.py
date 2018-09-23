#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from collections import namedtuple
from bes.fs import file_checksum, file_util

class source_item(namedtuple('source_item', 'filename, mtime, checksum')):
  
  def __new__(clazz, filename, mtime, checksum):
    return clazz.__bases__[0].__new__(clazz, filename, mtime, checksum)

  @classmethod
  def from_file(clazz, filename, directory = None):
    if directory:
      file_path = path.join(directory, filename)
    else:
      file_path = filename
    mtime = file_util.mtime(file_path)
    checksum = file_checksum.file_checksum(file_path, 'sha1')
    return clazz.__bases__[0].__new__(clazz, filename, mtime, checksum)
