#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path
from collections import namedtuple
from bes.common import check
from bes.fs import file_check, file_util

class package_file(namedtuple('package_file', 'filename, checksum, has_hardcoded_path')):

  def __new__(clazz, filename, checksum, has_hardcoded_path):
    check.check_string(filename)
    check.check_string(checksum)
    return clazz.__bases__[0].__new__(clazz, filename, checksum, bool(has_hardcoded_path))

  @classmethod
  def from_file(clazz, filename, has_hardcoded_path, root_dir = None, function_name = None):
    if root_dir:
      filepath = path.join(root_dir, filename)
    else:
      filepath = filename
    if path.islink(filepath):
      checksum = ''
    else:
      file_check.check_file(filepath)
      checksum = file_util.checksum(function_name or 'sha256', filepath)
    return clazz(filename, checksum, has_hardcoded_path)

  @classmethod
  def file_checksum(clazz, filename, has_hardcoded_path, function_name):
    return clazz.from_file(filename, has_hardcoded_path, function_name = function_name).checksum

  def to_list(self):
    return [ self.filename, self.checksum, self.has_hardcoded_path ]

check.register_class(package_file, include_seq = False)
