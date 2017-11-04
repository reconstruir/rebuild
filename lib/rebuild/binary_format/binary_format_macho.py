#!/usr/bin/env python
#-*- coding:utf-8 -*-

from collections import namedtuple
from .binary_format_base import binary_format_base, binary_format_object, binary_format_file
from bes.debug import hexdump

class binary_format_macho(binary_format_base):
  'Read the Mach-O binary format.'

  # Mach-O Refrences:
  #   https://en.wikipedia.org/wiki/List_of_file_signatures
  #   https://lowlevelbits.org/parsing-mach-o-files/
  #   /usr/include/mach-o/loader.h
  #   /usr/include/mach-o/fat.h

  # Magic numbers for Mach-O objects
  _MH_MAGIC = 0xfeedface
  _MH_CIGAM = 0xcefaedfe
  _MH_MAGIC_64 = 0xfeedfacf
  _MH_CIGAM_64 = 0xcffaedfe

  # Magic numbers for FAT objects
  _FAT_MAGIC = 0xcafebabe
  _FAT_CIGAM = 0xbebafeca
  
  # Whether to spew debugging info
  DEBUG = False
  #DEBUG = True

  DEBUG_HEXDUMP = False
  #DEBUG_HEXDUMP = True

  _MAGICS =  [ _MH_MAGIC, _MH_CIGAM ]
  _MAGICS_64 = [ _MH_MAGIC_64, _MH_CIGAM_64 ]
  _THIN_MAGICS = _MAGICS + _MAGICS_64
  _FAT_MAGICS = [ _FAT_MAGIC, _FAT_CIGAM ]
  _ALL_MAGICS = _THIN_MAGICS + _FAT_MAGICS

  _BE_MAGICS = [ _MH_MAGIC, _MH_MAGIC_64, _FAT_MAGIC ]
  _LE_MAGICS = [ _MH_CIGAM, _MH_CIGAM_64, _FAT_CIGAM ]

  # !<arch>\n
  _ARCHIVE_MAGIC = 0x213c617263683e0a
  
  MAGIC_FEEDFACE = 'feedface'
  MAGIC_CEFAEDFE = 'cefaedfe'
  MAGIC_FEEDFACF = 'feedfacf'
  MAGIC_CFFAEDFE = 'cffaedfe'
  MAGIC_CAFEBABE = 'cafebabe'
  MAGIC_BEBAFECA = 'bebafeca'
  MAGIC_ARCHIVE = '!<arch>\n'

  _MAGIC_TO_STRING = {
    _MH_MAGIC: MAGIC_FEEDFACE,
    _MH_CIGAM: MAGIC_CEFAEDFE,
    _MH_MAGIC_64: MAGIC_FEEDFACF,
    _MH_CIGAM_64: MAGIC_CFFAEDFE,
    _FAT_MAGIC: MAGIC_CAFEBABE,
    _FAT_CIGAM: MAGIC_BEBAFECA,
    _ARCHIVE_MAGIC: MAGIC_ARCHIVE,
  }

  _CPU_ARCH_ABI64 = 0x01000000

  # http://llvm.org/docs/doxygen/html/Support_2MachO_8h_source.html
  _CPU_TYPES = {
    -1: 'any',
    7: 'i386',
    7|_CPU_ARCH_ABI64: 'x86_64',
    8: 'mips',
    10: 'MC98000',
    12: 'arm',
    12|_CPU_ARCH_ABI64: 'arm64',
    14: 'sparc',
    16: 'alpha',
    18: 'powerpc',
    18|_CPU_ARCH_ABI64: 'powerpc64',
  }
  
  _FILE_TYPES = {
    0x1: binary_format_base.FILE_TYPE_OBJECT,
    0x2: binary_format_base.FILE_TYPE_EXECUTABLE,
    0x3: 'fvmlib',
    0x4: binary_format_base.FILE_TYPE_CORE,
    0x5: 'preload',
    0x6: binary_format_base.FILE_TYPE_SHARED_LIB,
    0x7: 'dylinker',
    0x8: 'bundle',
    0x9: 'dylib_stub',
    0xa: 'dsym',
    0xb: 'kext_bundle',
  }

  _fat_arch = namedtuple('fat_header', 'cpu_type,cpu_sub_type,offset,size,align')
  _mach_header = namedtuple('mach_header', 'magic,cpu_type,cpu_sub_type,file_type,ncmds,sizeofcmds,flags')

  def name(self):
    'Return the name of this binary format.'
    return 'macho'
  
  def is_binary(self, filename):
    'Return True if filename is a binary.'
    return self.read_info(filename) != None

  def read_magic(self, filename):
    'Return the Mach-O or FAT magic from filename or None if not an Mach-O file.'
    if self.DEBUG_HEXDUMP:
      print("filename=%s hexdump:\n%s\n" % (filename, hexdump.filename(filename)))
    elif self.DEBUG:
      print("filename=%s" % (filename))
    with open(filename, 'rb') as fin:
      magic = self.fin_read_magic(fin, 4, self.ENDIAN_BE)
      if not magic:
        return None
      if not magic in self._ALL_MAGICS:
        return None
      return self._MAGIC_TO_STRING[magic]

  def read_info(self, filename):
    'Return info about the Mach-O or FAT file.'
    if self.DEBUG_HEXDUMP:
      print("filename=%s hexdump:\n%s\n" % (filename, hexdump(filename)))
    elif self.DEBUG:
      print("filename=%s" % (filename))
    with open(filename, 'rb') as fin:
      container_magic = self.fin_read_magic(fin, 4, self.ENDIAN_BE)
      if not container_magic:
        return None
      if not container_magic in self._ALL_MAGICS:
        return None
      if self.DEBUG:
        print("      container_magic: %x" % (container_magic))
      is_fat = container_magic in self._FAT_MAGICS
      container_endian = self._determine_endian(container_magic)
      if self.DEBUG:
        print("               is_fat: %s" % (is_fat))
        print("           container_endian: %s" % (container_endian))
      if is_fat:
        return self._read_info_fat(filename, fin, container_magic, container_endian)
      else:
        return self._read_info_thin(filename, fin, container_magic, container_endian)

  def _read_info_thin(self, filename, fin, container_magic, container_endian):
    mach_header = self._read_mach_header(fin, container_magic, container_endian)
    obj = binary_format_object(self._MAGIC_TO_STRING[mach_header.magic],
                               self._CPU_TYPES[mach_header.cpu_type],
                               self._FILE_TYPES[mach_header.file_type])
    return binary_format_file('macho', None, False, [ obj ])

  def _read_info_fat(self, filename, fin, container_magic, container_endian):
    nfat_arch = self.unpack(fin, 4, container_endian)
    if self.DEBUG:
      print("            nfat_arch: %d" % (nfat_arch))
    if nfat_arch < 1:
      return None
    fat_headers = []
    for i in range(0, nfat_arch):
      fat_header = self._read_fat_arch(fin, container_endian)
      fat_headers.append(fat_header)
      if self.DEBUG:
        print("%d:       fat_cpu_type: %s" % (i, self._CPU_TYPES[fat_header.cpu_type]))
        print("%d:   fat_cpu_sub_type: %x - %d" % (i, fat_header.cpu_sub_type, fat_header.cpu_sub_type))
        print("%d:         fat_offset: %x - %d" % (i, fat_header.offset, fat_header.offset))
        print("%d:           fat_size: %x - %d" % (i, fat_header.size, fat_header.size))
        print("%d:          fat_align: %x - %d" % (i, fat_header.align, fat_header.align))
    objects = []
    for fat_header, index in zip(fat_headers, range(0, nfat_arch)):
      objects.append(self._read_info_one_object(filename, fin, fat_header, index, container_endian))
    info = binary_format_file('macho', container_magic, True, objects)
    return info

  def _read_info_one_object(self, filename, fin, fat_header, index, container_endian):
    fin.seek(fat_header.offset)
    object_magic = self.fin_read_magic(fin, 8, container_endian)
    if object_magic == self._ARCHIVE_MAGIC:
      obj = binary_format_object(self._MAGIC_TO_STRING[object_magic],
                                 self._CPU_TYPES[fat_header.cpu_type],
                                 self.FILE_TYPE_ARCHIVE)
    else:
      fin.seek(fat_header.offset)
      object_magic = self.fin_read_magic(fin, 4, container_endian)
      if not object_magic:
        return None
      if not object_magic in self._ALL_MAGICS:
        return None
      if self.DEBUG:
        print("%d:       object_magic: %s(%s)" % (index, self._MAGIC_TO_STRING[object_magic], type(object_magic)))
      assert object_magic in self._THIN_MAGICS
      object_endian = self._determine_endian(object_magic)
      mach_header = self._read_mach_header(fin, object_magic, object_endian)
      assert mach_header.magic == object_magic
      if self.DEBUG:
        print("%d:    object_cpu_type: %s" % (index, self._CPU_TYPES[mach_header.cpu_type]))
        print("%d:object_cpu_sub_type: %x - %d" % (index, mach_header.cpu_sub_type, mach_header.cpu_sub_type))
        print("%d:   object_file_type: %s" % (index, self._FILE_TYPES[mach_header.file_type]))
      obj = binary_format_object(self._MAGIC_TO_STRING[mach_header.magic],
                                 self._CPU_TYPES[mach_header.cpu_type],
                                 self._FILE_TYPES[mach_header.file_type])
    return obj
    
  def _read_fat_arch(self, fin, endian):
    fat_cpu_type = self.unpack(fin, 4, endian)
    fat_cpu_sub_type = self.unpack(fin, 4, endian)
    fat_offset = self.unpack(fin, 4, endian)
    fat_size = self.unpack(fin, 4, endian)
    fat_align = self.unpack(fin, 4, endian)
    return self._fat_arch(fat_cpu_type, fat_cpu_sub_type, fat_offset, fat_size, fat_align)

  def _read_mach_header(self, fin, magic, endian):
    cpu_type = self.unpack(fin, 4, endian)
    cpu_sub_type = self.unpack(fin, 4, endian)
    file_type = self.unpack(fin, 4, endian)
    ncmds = self.unpack(fin, 4, endian)
    sizeofcmds = self.unpack(fin, 4, endian)
    flags = self.unpack(fin, 4, endian)
    return self._mach_header(magic, cpu_type, cpu_sub_type, file_type, ncmds, sizeofcmds, flags)

  def _determine_endian(self, magic):
    'Return the correct endian for the given magic.'
    if magic in self._BE_MAGICS:
      return self.ENDIAN_BE
    assert magic in self._LE_MAGICS
    return self.ENDIAN_LE
