#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, shutil
from bes.system.execute import execute
from bes.system.host import host
from collections import namedtuple
from rebuild.toolchain.darwin.lipo import lipo
from bes.fs.dir_util import dir_util
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

class ar_replacement(object):
  'A replacement for the ar with fat support.'

  Tools = namedtuple('Tools', 'ar,libtool,lipo,ranlib')

  DEFAULT_TOOLS = Tools('ar', 'libtool', 'lipo', 'ranlib')
  
  @classmethod
  def contents(clazz, archive, tools = None):
    'Return the archive contents.'
    tools = tools or clazz.DEFAULT_TOOLS
    if clazz._archive_is_fat(archive):
      contents = clazz._contents_darwin_fat(archive, tools)
    else:
      contents = clazz._contents_with_ar(archive, tools)
    return contents

  @classmethod
  def extract(clazz, archive, dest_dir, tools = None):
    'Extract the archive into dest_dir.'
    tools = tools or clazz.DEFAULT_TOOLS
    if clazz._archive_is_fat(archive):
      clazz._extract_darwin_fat(archive, dest_dir, tools)
    else:
      clazz._extract_with_ar(archive, dest_dir, tools)

  @classmethod
  def replace(clazz, archive, objects, tools = None):
    'Replace an archive into dest_dir.'
    tools = tools or clazz.DEFAULT_TOOLS
    if host.is_macos():
      clazz._replace_darwin(archive, objects, tools)
    else:
      clazz._replace_with_ar(archive, objects, tools)

  @classmethod
  def _contents_with_ar(clazz, archive, tools):
    'Return the archive contents using ar.'
    cmd = [
      tools.ar,
      't',
      archive,
    ]
    cmd_flat = ' '.join(cmd)
    rv = execute.execute(cmd_flat)
    return rv.stdout.strip().split('\n')

  @classmethod
  def _contents_darwin_fat(clazz, archive, tools):
    'Return the archive contents for a fat archive on darwin.'
    tmp_dir = temp_file.make_temp_dir()
    thin_libs = clazz._fat_to_thin(archive, tmp_dir, tools)
    expected_contents = None
    for arch, lib in thin_libs:
      if not expected_contents:
        expected_contents = clazz._contents_with_ar(lib, tools)
        assert expected_contents
      else:
        contents = clazz._contents_with_ar(lib, tools)
        if contents != expected_contents:
          raise RuntimeError('Unexpected contents for thin lib: %s' % (lib))
    return expected_contents

  @classmethod
  def _extract_with_ar(clazz, archive, dest_dir, tools):
    'Return the archive contents using ar.'
    cmd = [
      tools.ar,
      'x',
      archive,
    ]
    cmd_flat = ' '.join(cmd)
    file_util.mkdir(dest_dir)
    execute.execute(cmd_flat, cwd = dest_dir)

  @classmethod
  def _extract_darwin_fat(clazz, archive, dest_dir, tools):
    'Extract fat archive.'
    tmp_dir = temp_file.make_temp_dir()
    thin_libs = clazz._fat_to_thin(archive, tmp_dir, tools)
    expected_contents = None
    file_util.mkdir(dest_dir)
    for arch, lib in thin_libs:
      objects_dir = lib + '.objdir'
      clazz._extract_with_ar(lib, objects_dir, tools)
      files = dir_util.list(objects_dir, relative = True)
      for f in files:
        src = path.join(objects_dir, f)
        dst_basename = arch + '_' + f
        dst = path.join(dest_dir, dst_basename)
        shutil.move(src, dst)

  @classmethod
  def _replace_with_ar(clazz, archive, objects, tools):
    'Replace an archive using ar.'
    cmd = [
      tools.ar,
      'r',
      archive,
    ] + objects
    cmd_flat = ' '.join(cmd)
    file_util.mkdir(path.dirname(archive))
    execute.execute(cmd_flat)

  @classmethod
  def _replace_darwin(clazz, archive, objects, tools):
    'Replace an archive on darwin using libtool.'
    cmd = [
      tools.libtool,
      '-static',
      '-o',
      archive,
    ]
    if path.exists(archive):
      cmd += [ archive ]
    cmd += objects
    cmd_flat = ' '.join(cmd)
    parent_dir = path.dirname(archive)
    if parent_dir:
      file_util.mkdir(parent_dir)
    execute.execute(cmd_flat)
        
  FatToThinItem = namedtuple('FatToThinItem', 'arch,filename')
  @classmethod
  def _fat_to_thin(clazz, archive, dest_dir, tools):
    archs = lipo.archs(archive, lipo_exe = tools.lipo)
    if not archs:
      raise RuntimeError('Not a fat library: %s' % (archive))
    result = []
    for arch in archs:
      tmp_basename = arch + '_' + path.basename(archive)
      tmp_filename = path.join(dest_dir, tmp_basename)
      file_util.mkdir(dest_dir)
      lipo.fat_to_thin(archive, tmp_filename, arch, lipo_exe = tools.lipo)
      result.append(clazz.FatToThinItem(arch, tmp_filename))
    return result

  @classmethod
  def _archive_is_fat(clazz, archive):
    'Return True if the archive is fat (and running on darwin)'
    return host.is_macos() and lipo.archive_is_fat(archive)
