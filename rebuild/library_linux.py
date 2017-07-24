#!/usr/bin/env python
#-*- coding:utf-8 -*-

from library_base import library_base

import os.path as path
from bes.common import Shell, string_util
from binary_format_elf import binary_format_elf

class library_linux(library_base):

  def __init__(self):
    super(library_linux, self).__init__()
    self._format = binary_format_elf()
    
  def is_shared_library(self, filename):
    'Return True if filename is a shared library.'
    return self._format.file_is_of_type(filename, binary_format_elf.FILE_TYPE_SHARED_LIB)

  def is_static_library(self, filename):
    'Return True if filename is a shared library.'
    return self._format.file_is_of_type(filename, binary_format_elf.FILE_TYPE_ARCHIVE)

  def dependencies(self, filename):
    'Return a list of dependencies for filename (executable or shared lib) or None if not applicable.'
    types = [ binary_format_elf.FILE_TYPE_EXECUTABLE, binary_format_elf.FILE_TYPE_SHARED_LIB ]
    if not binary_format_elf().file_is_of_type(filename, types):
      return None
    cmd = [ 'ldd', filename ]
    rv = Shell.execute(cmd)
    assert rv.stdout.find('not a dynamic executable') == -1
    lines = rv.stdout.split('\n')
    deps = [ self.__parse_ldd_line(line) for line in lines ]
    deps = [ d for d in deps if d ]
    return sorted(deps)

  def __parse_ldd_line(self, line):
    line = line.strip()
    if not line:
      return None
    parts = string_util.split_by_white_space(line, strip = True)
    if len(parts) >= 2 and parts[1] == '=>' and path.exists(parts[2]):
      return parts[2]
    elif path.exists(parts[0]):
      return parts[0]
    else:
      return None

  def shared_extension(self):
    'Return the shared library extension.'
    return 'so'

  def static_extension(self):
    'Return the static library extension.'
    return 'a'

  def shared_prefix(self):
    'Return the shared library prefix.'
    return 'lib'

  def static_prefix(self):
    'Return the static library prefix.'
    return 'lib'
