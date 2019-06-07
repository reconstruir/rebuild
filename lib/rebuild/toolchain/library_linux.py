#!/usr/bin/env python
#-*- coding:utf-8 -*-

from .library_base import library_base
import os.path as path
from bes.common.string_util import string_util
from bes.system.execute import execute
from rebuild.binary_format import binary_format_elf

class library_linux(library_base):

  _format = binary_format_elf()

  @classmethod
  def is_shared_library(clazz, filename):
    'Return True if filename is a shared library.'
    return clazz._format.file_is_of_type(filename, binary_format_elf.FILE_TYPE_SHARED_LIB)

  @classmethod
  def is_static_library(clazz, filename):
    'Return True if filename is a shared library.'
    return clazz._format.file_is_of_type(filename, binary_format_elf.FILE_TYPE_ARCHIVE)

  @classmethod
  def dependencies(clazz, filename):
    'Return a list of dependencies for filename (executable or shared lib) or None if not applicable.'
    types = [ binary_format_elf.FILE_TYPE_EXECUTABLE, binary_format_elf.FILE_TYPE_SHARED_LIB ]
    if not binary_format_elf().file_is_of_type(filename, types):
      return None
    cmd = [ 'ldd', filename ]
    rv = execute.execute(cmd)
    assert rv.stdout.find('not a dynamic executable') == -1
    lines = rv.stdout.split('\n')
    deps = [ clazz.__parse_ldd_line(line) for line in lines ]
    deps = [ d for d in deps if d ]
    return sorted(deps)

  @classmethod
  def __parse_ldd_line(clazz, line):
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

  @classmethod
  def shared_extension(clazz):
    'Return the shared library extension.'
    return 'so'

  @classmethod
  def static_extension(clazz):
    'Return the static library extension.'
    return 'a'

  @classmethod
  def shared_prefix(clazz):
    'Return the shared library prefix.'
    return 'lib'

  @classmethod
  def static_prefix(clazz):
    'Return the static library prefix.'
    return 'lib'

  @classmethod
  def binary_format_name(self):
    'The name of the binary format (usually elf or macho).'
    return 'elf'
