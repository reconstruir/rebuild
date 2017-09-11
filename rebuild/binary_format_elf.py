#!/usr/bin/env python
#-*- coding:utf-8 -*-

from binary_format_base import binary_format_base, binary_format_object, binary_format_file
from bes.debug import hexdump

class binary_format_elf(binary_format_base):
  'Read the ELF binary format.'

  # ELF Refrences:
  #   https://en.wikipedia.org/wiki/Executable_and_Linkable_Format#File_header
  #   /usr/include/linux/elf-em.h

  MAGIC_ELF = '7f454c46'
  
  # Magic numbers for Mach-O objects
  __MAGIC_NUMBER_ELF = 0x7f454c46
  
  # Whether to spew debugging info
  DEBUG = False
  #DEBUG = True

  DEBUG_HEXDUMP = False
  #DEBUG_HEXDUMP = True

  __MAGIC_TO_STRING = {
    __MAGIC_NUMBER_ELF: MAGIC_ELF,
  }

  __FILE_TYPES = {
    0x1: binary_format_base.FILE_TYPE_OBJECT,
    0x2: binary_format_base.FILE_TYPE_EXECUTABLE,
    0x3: binary_format_base.FILE_TYPE_SHARED_LIB,
    0x4: binary_format_base.FILE_TYPE_CORE,
  }

  __MACHINES = {
    0x0: 'none',
    0x1: 'm32',
    0x2: 'sparc',
    0x3: '386',
    0x4: '68k',
    0x5: '88k',
    0x6: '486',
    0x7: '860',
    0x8: 'mips',
    0xa: 'mips_rs3_le',
    0xa: 'mips_rs4_be',
    0xf: 'parisc',
    0x12: 'sparc32plus',
    0x14: 'ppc',
    0x15: 'ppc64',
    0x17: 'spu',
    0x28: 'arm',
    0x2a: 'sh',
    0x2b: 'sparcv9',
    0x32: 'ia_64',
    0x3e: 'x86_64',
    0x16: 's390',
    0x4c: 'cris',
    0x57: 'v850',
    0x58: 'm32r',
    0x59: 'mn10300',
    0x6a: 'blackfin',
    0x8c: 'ti_c6000',
    0xb7: 'aarch64',
    0x5441: 'frv',
    0x18ad: 'avr32',
    0x9026: 'alpha',
    0x9080: 'cygnus_v850',
    0x9041: 'cygnus_m32r',
    0xa390: 's390_old',
    0xbeef: 'cygnus_mn10300',
  }
  
  __ELF_ENDIAN_MAP = {
    0x1: binary_format_base.ENDIAN_LE,
    0x2: binary_format_base.ENDIAN_BE,
  }
  __ELF_VALID_ENDIANS = __ELF_ENDIAN_MAP.keys()

  def is_binary(self, filename):
    'Return True if filename is a binary.'
    return self.read_info(filename) != None

  def read_magic(self, filename):
    'Return the Mach-O or FAT magic from filename or None if not a Mach-O file.'
    with open(filename, 'rb') as fin:
      magic = self.fin_read_magic(fin, 4, self.ENDIAN_BE)
      if not magic:
        return None
      if not magic in [ self.__MAGIC_NUMBER_ELF ]:
        return None
      return self.__MAGIC_TO_STRING[magic]

  def read_info(self, filename):
    'Return info about the ELF binary file or None if it is not ELF.'
    if self.DEBUG_HEXDUMP:
      print("filename=%s hexdump:\n%s\n" % (filename, hexdump.filename(filename)))
    elif self.DEBUG:
      print("filename=%s" % (filename))
    with open(filename, 'rb') as fin:
      magic = self.fin_read_magic(fin, 4, self.ENDIAN_BE)
      if not magic:
        return None
      if not magic in [ self.__MAGIC_NUMBER_ELF ]:
        return None
      if self.DEBUG:
        print("                magic: %x" % (magic))
      elf_class = self.unpack(fin, 1, self.ENDIAN_BE)
      elf_endian = self.unpack(fin, 1, self.ENDIAN_BE)
      endian = self.__ELF_ENDIAN_MAP[elf_endian]
      elf_version = self.unpack(fin, 1, self.ENDIAN_BE)
      elf_os_abi = self.unpack(fin, 1, self.ENDIAN_BE)
      elf_abi_version = self.unpack(fin, 1, self.ENDIAN_BE)
      # 7 unused pad bytes
      fin.read(7)
      # starting with offset 0x10 (elf_type) the endian needs to be that given in the elf object itself
      elf_type = self.unpack(fin, 2, endian)
      elf_machine = self.unpack(fin, 2, endian)
      assert elf_endian in self.__ELF_VALID_ENDIANS
      if self.DEBUG:
        print("            elf_class: %x" % (elf_class))
        print("           elf_endian: %x" % (elf_endian))
        print("               endian: %s" % (endian))
        print("          elf_version: %x" % (elf_version))
        print("           elf_os_abi: %x" % (elf_version))
        print("      elf_abi_version: %x" % (elf_abi_version))
        print("             elf_type: %x" % (elf_type))
        print("          elf_machine: %x" % (elf_machine))
      if self.__MACHINES.has_key(elf_machine):
        elf_machine_name = self.__MACHINES[elf_machine]
      else:
        elf_machine_name = 'unknown'
      obj = binary_format_object(self.__MAGIC_TO_STRING[magic],
                                 elf_machine_name,
                                 self.__FILE_TYPES[elf_type])
      info = binary_format_file('elf', None, False, [ obj ])
      return info

  def magic_to_string(self, magic):
    return self.MAGIC_TO_STRING.get(magic, '')

  def cpu_type_to_string(self, cpu_type):
    return self.CPU_TYPES.get(cpu_type, 'unknown')

  def file_type_to_string(self, file_type):
    return self.FILE_TYPES.get(file_type, 'unknown')
