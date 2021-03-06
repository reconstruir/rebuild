#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, re

from bes.common import algorithm, object_util, string_util
from bes.system import execute
from bes.fs import dir_util, file_find, file_util, temp_file
from bes.archive import archiver

class archive_util(object):

  @classmethod
  def autoconf_help(clazz, tarball):
    'Return the output of configure --help for an autoconf archive.'
    tmp_dir = temp_file.make_temp_dir()
    archiver.extract(tarball, tmp_dir, strip_common_ancestor = True)
    confiugure_path = path.join(tmp_dir, 'configure')
    if not path.exists(confiugure_path):
      raise RuntimeError('No configure script found in %s' % (tarball))
    help = execute.execute('./configure --help', cwd = tmp_dir, shell = True, raise_error = False).stdout
    file_util.remove(tmp_dir)
    return help

  ORIGINAL_DIR_TAIL = '.orig'

  @classmethod
  def patch_prepare(clazz, tarball, dest_dir):
    'Prepare to work on patches by extracting tarball to $name-$version.orig and $name-$version.'
    common_base = archiver.common_base(tarball)
    if not common_base:
      raise RuntimeError('No common base found for %s' % (tarball))
    dir1 = path.join(dest_dir, common_base)
    if path.exists(dir1):
      raise RuntimeError('Dir already exists: %s' % (dir1))
    dir2 = dir1 + clazz.ORIGINAL_DIR_TAIL
    if path.exists(dir2):
      raise RuntimeError('Dir already exists: %s' % (dir2))
    archiver.extract(tarball, dir1, strip_common_ancestor = True)
    archiver.extract(tarball, dir2, strip_common_ancestor = True)
    
  @classmethod
  def patch_make(clazz, working_dir):
    'Create a patch out of 2 directories one ending in .orig.'
    dirs = dir_util.list(working_dir, relative = True)
    if len(dirs) != 2:
      raise RuntimeError('Found more than 2 directories in %s' % (working_dir))

    if not dirs[1].endswith(clazz.ORIGINAL_DIR_TAIL):
      raise RuntimeError('Dir 2 should end in .orig instead it is %s' % (dir2))

    base_dir = file_util.remove_tail(dirs[1], clazz.ORIGINAL_DIR_TAIL)
    if string_util.remove_tail(dirs[1], clazz.ORIGINAL_DIR_TAIL) != dirs[0]:
      raise RuntimeError('Dir 1 and 2 dont have the same name: %s %s' % (dirs[1], dirs[0]))
    cmd = 'diff -ur %s %s --exclude="*~" --exclude=".#*" --exclude="#*"' % (dirs[1], dirs[0])
    patch = execute.execute(cmd, cwd = working_dir, raise_error = False).stdout
    return patch.strip()
    
  @classmethod
  def grep(clazz, tarball, pattern):
    'Return the output of ag (silver searcher) for an archive.'
    tmp_dir = temp_file.make_temp_dir()
    archiver.extract(tarball, tmp_dir, strip_common_ancestor = True)
    result = execute.execute('ag %s .' % (pattern), cwd = tmp_dir, shell = True, raise_error = False).stdout
    file_util.remove(tmp_dir)
    return result

  @classmethod
  def diff(clazz, archive1, archive2, strip_common_ancestor = False):
    'Return the output of diffing the contents of 2 archives.'

    members1 = archiver.members(archive1)
    members2 = archiver.members(archive2)

    content1 = '\n'.join(members1)
    content2 = '\n'.join(members2)

    tmp_file1 = temp_file.make_temp_file(content = content1)
    tmp_file2 = temp_file.make_temp_file(content = content2)

    rv = execute.execute('diff -u %s %s' % (tmp_file1, tmp_file2), raise_error = False)

    return rv.stdout
