#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path as path
from library_base import library_base
from bes.common import Shell
from binary_format_macho import binary_format_macho

class library_macos(library_base):

  _format = binary_format_macho()
    
  @classmethod
  def is_shared_library(clazz, filename):
    'Return True if filename is a shared library.'
    return clazz._format.file_is_of_type(filename, binary_format_macho.FILE_TYPE_SHARED_LIB)

  @classmethod
  def is_static_library(clazz, filename):
    'Return True if filename is a shared library.'
    return clazz._format.file_is_of_type(filename, binary_format_macho.FILE_TYPE_ARCHIVE)

  @classmethod
  def dependencies(clazz, filename):
    'Return a list of dependencies for filename (executable or shared lib) or None if not applicable.'
    filename = path.abspath(filename)
    types = [ binary_format_macho.FILE_TYPE_EXECUTABLE, binary_format_macho.FILE_TYPE_SHARED_LIB ]
    if not binary_format_macho().file_is_of_type(filename, types):
      return None
    cmd = [ 'otool', '-L', filename ]
    rv = Shell.execute(cmd)
    assert rv.stdout.find('is not an object file') == -1
    lines = rv.stdout.split('\n')
    if len(lines) < 2:
      return None
    assert lines[0].endswith(filename + ':')
    deps = [ l.partition(' ')[0].strip() for l in lines[ 1:] ]
    deps = [ l for l in deps if l ]
    if filename in deps:
      deps.remove(filename)
    return sorted(deps)

  @classmethod
  def shared_extension(clazz):
    'Return the shared library extension.'
    return 'dylib'

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
