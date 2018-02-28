#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from bes.common import object_util, string_util
from bes.system import execute

class lipo(object):

  LIPO_EXE = 'lipo'
  FAT_EXPRESSION = 'Architectures in the fat file: .+ are: (.*)\w*'
  THIN_EXPRESSION = 'Non-fat file: .+ is architecture: (.*)'
  POSSIBLE_ARCHS = [ 'arm64', 'armv7', 'i386', 'x86_64' ]

  @classmethod
  def archs(clazz, archive, lipo_exe = None):
    rv = clazz.__call_lipo_info(archive, lipo_exe = lipo_exe)
    ex = re.findall(clazz.FAT_EXPRESSION, rv.stdout)
    if ex:
      archs = string_util.split_by_white_space(ex[0])
    else:
      ex = re.findall(clazz.THIN_EXPRESSION, rv.stdout)
      if len(ex) != 1:
        raise RuntimeError('Invalid archive for lipo: %s' % (archive))
      archs = ex
    return sorted([ arch.strip() for arch in archs ])

  @classmethod
  def is_valid_object(clazz, filename, lipo_exe = None):
    'Return True of the given object filename is something lipo can work with.'
    try:
      rv = clazz.__call_lipo_info(filename, lipo_exe = lipo_exe)
      return rv.exit_code == 0
    except:
      return False
  
  @classmethod
  def archive_is_fat(clazz, archive, lipo_exe = None):
    return len(clazz.archs(archive, lipo_exe = lipo_exe)) > 1
  
  @classmethod
  def fat_to_thin(clazz, fat_archive, thin_archive, arch, lipo_exe = None):
    if arch not in clazz.POSSIBLE_ARCHS:
      raise RuntimeError('Invalid arch: %s' % (arch))
    args = [ '-thin', arch, '-o', thin_archive, fat_archive ]
    clazz.__call_lipo(args, lipo_exe = lipo_exe)

  @classmethod
  def thin_to_fat(clazz, thin_objects, fat_object, lipo_exe = None):
    if not object_util.is_iterable(thin_objects):
      raise RuntimeError('thin_objects are not iterable: %s' % (thin_objects))
    args = [ '-create' ] + thin_objects + [ '-o', fat_object ]
    clazz.__call_lipo(args, lipo_exe = lipo_exe)
    
  @classmethod
  def __call_lipo(clazz, args, lipo_exe = None):
    exe = lipo_exe or clazz.LIPO_EXE
    cmd = [ exe ] + args
    return execute.execute(cmd, shell = False)

  @classmethod
  def __call_lipo_info(clazz, filename, lipo_exe = None):
    'Return the output of lipo -info $filename.'
    args = [ '-info', filename ]
    return clazz.__call_lipo(args, lipo_exe = lipo_exe)
