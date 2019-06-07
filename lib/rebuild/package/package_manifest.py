#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common.check import check

from .package_file_list import package_file_list
from .sql_encoding import sql_encoding

class package_manifest(namedtuple('package_manifest', 'files, env_files, contents_checksum')):

  def __new__(clazz, files, env_files, contents_checksum = None):

    files = files or package_file_list()
    check.check_package_file_list(files)

    env_files = env_files or package_file_list()
    check.check_package_file_list(env_files)

    if contents_checksum:
      check.check_string(contents_checksum)
    else:
      contents_checksum = (files + env_files).checksum()

    return clazz.__bases__[0].__new__(clazz, files, env_files, contents_checksum)

  @classmethod
  def parse_dict(clazz, o):
    return clazz(package_file_list.from_simple_list(o['files']),
                 package_file_list.from_simple_list(o['env_files']),
                 o['contents_checksum'])
  
  def to_simple_dict(self):
    'Return a simplified dict suitable for json encoding.'
    return {
      'files': self.files.to_simple_list(),
      'env_files': self.env_files.to_simple_list(),
      'contents_checksum': self.contents_checksum,
    }
  
  def to_sql_dict(self):
    'Return a dict suitable to use directly with sqlite insert commands'
    d =  {
      'contents_checksum': sql_encoding.encode_string(self.contents_checksum),
    }
    return d

check.register_class(package_manifest, include_seq = False)
