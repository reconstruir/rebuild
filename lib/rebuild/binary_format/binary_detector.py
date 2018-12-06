#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .binary_format_macho import binary_format_macho
from .binary_format_elf import binary_format_elf

from bes.fs import file_find

class binary_detector(object):
  'Detect binaries (executables and shared libraries).'

  # Whether to spew debugging info
  DEBUG = False

  _FORMATS = [
    binary_format_macho(),
    binary_format_elf(),
  ]

  # both binary_format_macho and binary_format_elf subclass from both binary_format_base
  # where these constants are define so we can choose either one here
  FILE_TYPE_EXECUTABLE = binary_format_macho.FILE_TYPE_EXECUTABLE
  FILE_TYPE_SHARED_LIB = binary_format_macho.FILE_TYPE_SHARED_LIB

  _STRIPPABLE_TYPES = [
    FILE_TYPE_EXECUTABLE,
    FILE_TYPE_SHARED_LIB,
  ]
  
  @classmethod
  def find_strippable_binaries(clazz, d, format_name = None):
    'Recursively find binaries that can be stripped in d.'
    files = file_find.find(d, relative = False)
    return [ f for f in files if clazz.is_strippable(f, format_name) ]

  @classmethod
  def is_strippable(clazz, filename, format_name = None):
    'Return True if filename is a binary type that can be stripped (exe or dylib).'
    if clazz._ignore_file(filename):
      return False
    if format_name:
      formats = [ f for f in clazz._FORMATS if f.name() == format_name ]
    else:
      formats = clazz._FORMATS
    for fmt in formats:
      if fmt.file_is_of_type(filename, clazz._STRIPPABLE_TYPES):
        return True
    return False

  @classmethod
  def is_executable(clazz, filename, format_name = None):
    'Return True if filename is a binary executable.'
    if clazz._ignore_file(filename):
      return False
    if format_name:
      formats = [ f for f in clazz._FORMATS if f.name() == format_name ]
    else:
      formats = clazz._FORMATS
    for fmt in formats:
      if fmt.file_is_of_type(filename, clazz.FILE_TYPE_EXECUTABLE):
        return True
    return False

  #FIXME: this class breaks for java class files need to differnetiate them.
  @classmethod
  def _ignore_file(clazz, filename):
    'Return True if filename is a binary executable.'
    assert filename
    return filename.lower().endswith('.class')
