#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path as path
from library_base import library_base
from bes.common import Shell
from binary_format_macho import binary_format_macho

class library_macos(library_base):

  def __init__(self):
    super(library_macos, self).__init__()
    self._format = binary_format_macho()
    
  def is_shared_library(self, filename):
    'Return True if filename is a shared library.'
    return self._format.file_is_of_type(filename, binary_format_macho.FILE_TYPE_SHARED_LIB)

  def is_static_library(self, filename):
    'Return True if filename is a shared library.'
    return self._format.file_is_of_type(filename, binary_format_macho.FILE_TYPE_ARCHIVE)

  def dependencies(self, filename):
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

  def shared_extension(self):
    'Return the shared library extension.'
    return 'dylib'

  def static_extension(self):
    'Return the static library extension.'
    return 'a'

  def shared_prefix(self):
    'Return the shared library prefix.'
    return 'lib'

  def static_prefix(self):
    'Return the static library prefix.'
    return 'lib'
