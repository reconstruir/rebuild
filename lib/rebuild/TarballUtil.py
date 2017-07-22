#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, re

from bes.common import algorithm, object_util, Shell, string_util
from bes.fs import dir_util, file_find, file_util, temp_file
from bes.archive import archiver

class TarballUtil(object):

  @classmethod
  def find(clazz, root_dir, name, version):
    filenames = file_find.find(root_dir, max_depth = 1, relative = False, file_type = file_find.FILE | file_find.LINK)
    return clazz.find_in_list(filenames, name, version)

  @classmethod
  def find_in_list(clazz, filenames, name, version):
    'Find the filenames that match name and version.'

    name_replacements = {
      'lib': '',
    }
    name_prefix = clazz.__name_prefix(name)
    if name_prefix:
      name_replacements[name_prefix] = ''
    name = re.escape(string_util.replace(name, name_replacements))
    version = re.escape(version)
    version = version.replace('\\.', '.')
    version = version.replace('\\-', '.')

    exp1 = r'.*%s.*%s.*' % (name, version)

    expressions  = [
      re.compile(exp1),
      re.compile(exp1, re.IGNORECASE),
    ]
    result = []
    for filename in filenames:
      for expression in expressions:
        if expression.match(filename):
          result.append(filename)
    return sorted(algorithm.unique(result))

  @classmethod
  def __name_prefix(clazz, name):
    'Return the name prefix if it exists.  foo_xyz => foo;  xyz => None.'
    i = name.find('_')
    if i < 0:
      return None
    return name[0 : i + 1]
  
  @classmethod
  def extract(clazz, tarballs, dest_dir, base_dir, strip_common_base):
    tarballs = object_util.listify(tarballs)
    for tarball in tarballs:
      archiver.extract(tarball,
                       dest_dir,
                       base_dir = base_dir,
                       strip_common_base = strip_common_base)
  @classmethod
  def autoconf_help(clazz, tarball):
    'Return the output of configure --help for an autoconf archive.'
    tmp_dir = temp_file.make_temp_dir()
    archiver.extract(tarball, tmp_dir, strip_common_base = True)
    confiugure_path = path.join(tmp_dir, 'configure')
    if not path.exists(confiugure_path):
      raise RuntimeError('No configure script found in %s' % (tarball))
    help = Shell.execute('./configure --help', cwd = tmp_dir, shell = True, raise_error = False).stdout
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
    archiver.extract(tarball, dir1, strip_common_base = True)
    archiver.extract(tarball, dir2, strip_common_base = True)
    
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
    patch = Shell.execute(cmd, cwd = working_dir, raise_error = False).stdout
    return patch.strip()
    
  @classmethod
  def grep(clazz, tarball, pattern):
    'Return the output of ag (silver searcher) for an archive.'
    tmp_dir = temp_file.make_temp_dir()
    archiver.extract(tarball, tmp_dir, strip_common_base = True)
    result = Shell.execute('ag %s .' % (pattern), cwd = tmp_dir, shell = True, raise_error = False).stdout
    file_util.remove(tmp_dir)
    return result

  @classmethod
  def diff(clazz, archive1, archive2, strip_common_base = False):
    'Return the output of diffing the contents of 2 archives.'

    members1 = archiver.members(archive1)
    members2 = archiver.members(archive2)

    content1 = '\n'.join(members1)
    content2 = '\n'.join(members2)

    tmp_file1 = temp_file.make_temp_file(content = content1)
    tmp_file2 = temp_file.make_temp_file(content = content2)

    rv = Shell.execute('diff -u %s %s' % (tmp_file1, tmp_file2), raise_error = False)

    return rv.stdout
