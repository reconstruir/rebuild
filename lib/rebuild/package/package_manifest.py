#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.fs.dir_util import dir_util
from bes.fs.file_find import file_find
from bes.system.execute import execute
from bes.system.host import host
from bes.text.text_line_parser import text_line_parser

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

  @classmethod
  def determine_files(clazz, stage_dir):
    '''Return the list of files to package.
    Maybe could do some filtering here.
    Using find on unix because its faster that bes.fs.file_find.'
    '''
    if host.is_unix():
      return clazz._determine_files_unix(stage_dir)
    elif host.is_windows():
      return clazz._determine_files_windows(stage_dir)
    else:
      host.raise_unsupported_system()

  @classmethod
  def _determine_files_unix(clazz, stage_dir):
    stuff = dir_util.list(stage_dir, relative = True)
    rv = execute.execute([ 'find' ] + stuff + ['-type', 'f' ], cwd = stage_dir)
    files = text_line_parser.parse_lines(rv.stdout, strip_text = True, remove_empties = True)
    rv = execute.execute([ 'find' ] + stuff + ['-type', 'l' ], cwd = stage_dir)
    links = text_line_parser.parse_lines(rv.stdout, strip_text = True, remove_empties = True)
    return sorted(files + links)
  
  @classmethod
  def _determine_files_windows(clazz, stage_dir):
    return file_find.find(stage_dir, relative = True, file_type = file_find.FILE | file_find.LINK)
  
check.register_class(package_manifest, include_seq = False)
