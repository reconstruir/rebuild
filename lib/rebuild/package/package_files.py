#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.fs import file_checksum_list
from bes.common import check
from .util import util

class package_files(namedtuple('package_files', 'files, env_files, files_checksum, env_files_checksum')):

  def __new__(clazz, files, env_files, files_checksum = None, env_files_checksum = None):

    files = files or file_checksum_list()
    check.check_file_checksum_list(files)

    env_files = env_files or file_checksum_list()
    check.check_file_checksum_list(env_files)

    if files_checksum:
      check.check_string(files_checksum)
    files_checksum = files_checksum or files.checksum()

    if env_files_checksum:
      check.check_string(env_files_checksum)
    env_files_checksum = env_files_checksum or env_files.checksum()
    
    return clazz.__bases__[0].__new__(clazz, files, env_files, files_checksum, env_files_checksum)

  @classmethod
  def parse_dict(clazz, o):
    return clazz(file_checksum_list.from_simple_list(o['files']),
                 file_checksum_list.from_simple_list(o['env_files']),
                 o['files_checksum'],
                 o['env_files_checksum'])
  
  def to_simple_dict(self):
    'Return a simplified dict suitable for json encoding.'
    return {
      'files': self.files.to_simple_list(),
      'env_files': self.env_files.to_simple_list(),
      'files_checksum': self.files_checksum,
      'env_files_checksum': self.env_files_checksum,
    }
  
  def to_sql_dict(self):
    'Return a dict suitable to use directly with sqlite insert commands'
    d =  {
      'files_checksum': util.sql_encode_string(self.files_checksum),
      'env_files_checksum': util.sql_encode_string(self.env_files_checksum),
    }
    return d

check.register_class(package_files, include_seq = False)
