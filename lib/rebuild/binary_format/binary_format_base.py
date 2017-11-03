#!/usr/bin/env python
#-*- coding:utf-8 -*-

import struct
from collections import namedtuple
from abc import abstractmethod, ABCMeta
from bes.common import object_util
from bes.system.compat import with_metaclass

binary_format_object = namedtuple('binary_format_object', 'magic,cpu_type,file_type')
binary_format_file = namedtuple('binary_format_file', 'format,magic,is_fat,objects')

class binary_format_base(with_metaclass(ABCMeta, object)):
  'Base class for binary formats.'

  FILE_TYPE_OBJECT = 'object'
  FILE_TYPE_EXECUTABLE = 'executable'
  FILE_TYPE_SHARED_LIB = 'shared_lib'
  FILE_TYPE_CORE = 'core'
  FILE_TYPE_ARCHIVE = 'archive'

  ENDIAN_LE = 'le'
  ENDIAN_BE = 'be'

  @abstractmethod
  def name(self):
    'Return the name of this binary format.'
    pass
  
  @abstractmethod
  def is_binary(self, filename):
    'Return True if filename is a binary.'
    pass

  @abstractmethod
  def read_magic(self, filename):
    'Return the Mach-O or FAT magic from filename or None if not a Mach-O file.'
    pass
  
  @abstractmethod
  def read_info(self, filename):
    'Return info about filename filename as binary_format_file or None if not applicable.'
    pass

  def file_is_of_type(self, filename, types):
    'Return True of file is of one of the given type or types.'
    types = object_util.listify(types)
    return self.file_type(filename) in types

  def file_type(self, filename):
    'Return the file type for filename or None if its not a valid binary.'
    info = self.read_info(filename)
    if not info:
      return False
    assert len(info.objects) >= 1
    return info.objects[0].file_type

  def endian_is_valid(self, endian):
    'Return True if endian is a valid endian.'
    return endian in [ self.ENDIAN_LE, self.ENDIAN_BE ]

  __STRUCT_ENDIANS = { ENDIAN_LE: '<', ENDIAN_BE: '>' }
  __STRUCT_FORMATS = { 1: 'B', 2: 'H', 4: 'I', 8: 'Q' }
  __STRUCT_LENGTHS = __STRUCT_FORMATS.keys()

  def unpack(self, fin, n, endian):
    'Read and unpack n bytes from fin and return the integer value for the data.'
    assert n in self.__STRUCT_LENGTHS
    format = '%s%s' % (self.__STRUCT_ENDIANS[endian], self.__STRUCT_FORMATS[n])
    return struct.unpack(format, fin.read(n))[0]

  def fin_read_magic(self, fin, n, endian):
    'Read and validate a 4 byte magic number from the given stream and return it or None if not valid.'
    try:
      magic = self.unpack(fin, n, self.ENDIAN_BE)
    # Handle struct errors only (such as short reads for files smaller than 4 bytes)
    except struct.error as ex:
      magic = None
    return magic
