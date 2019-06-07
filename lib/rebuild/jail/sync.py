#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import errno, os, os.path as path, shutil, stat
from bes.fs.file_util import file_util

class sync(object):

  @classmethod
  def sync_files(clazz, src_dir, dst_dir, files, label):
    'Sync 2 directories using hard links where possible.'
    file_util.mkdir(dst_dir)
    for f in files:
      src_filename = path.join(src_dir, f)
      dst_filename = path.join(dst_dir, file_util.lstrip_sep(f))
      clazz.__sync_file(src_filename, dst_filename, label)

  @classmethod
  def __sync_file(clazz, src_filename, dst_filename, label):
    'Create hard link from src_filename to dst_filename.'
    #print "__sync_file(%s, %s)" % (src_filename, dst_filename)
    
    try:
      st = os.lstat(src_filename)
    except OSError as ex:
      if ex.errno == errno.ENOENT:
        print(('warning: missing: %s - %s' % (src_filename, label)))
        return
      elif ex.errno == errno.EACCES:
        print(('warning: access denied: %s - %s' % (src_filename, label)))
        return
      else:
        raise

    if stat.S_ISREG(st.st_mode):
      try:
        clazz.__sync_file_regular_with_hardlink(src_filename, dst_filename, label)
      except OSError as ex:
        if ex.errno == errno.EXDEV:
          clazz.__sync_file_regular_with_copy(src_filename, dst_filename, label)
        else:
          raise
    elif stat.S_ISDIR(st.st_mode):
      clazz.__sync_file_dir(src_filename, dst_filename, label)
    elif stat.S_ISLNK(st.st_mode):
      clazz.__sync_file_soft_link(src_filename, dst_filename, label)
    else:
      raise RuntimeError('unknown file type: %s - %s' % (src_filename, label))

  @classmethod
  def __sync_file_regular_with_hardlink(clazz, src_filename, dst_filename, label):
    'Sync a regular file using hard links.'
    try:
      os.link(src_filename, dst_filename)
    except OSError as ex:
      if ex.errno == errno.EEXIST:
        # ignore file exists
        print(('warning: file already exists: %s - %s' % (src_filename, label)))
      else:
        raise

  @classmethod
  def __sync_file_regular_with_copy(clazz, src_filename, dst_filename, label):
    'Sync a regular file by copying it.'
    try:
      shutil.copy2(src_filename, dst_filename)
    except OSError as ex:
      print(('warning: caught: %s%s' % (ex)))
      raise

  @classmethod
  def __sync_file_soft_link(clazz, src_filename, dst_filename, label):
    'Sync a soft link.'
    real_source = os.readlink(src_filename)
    try:
      os.symlink(real_source, dst_filename)
    except OSError as ex:
      if ex.errno == errno.EEXIST:
        # ignore file exists
        print(('warning: link already exists: %s - %s' % (src_filename, label)))
      else:
        raise

  @classmethod
  def __sync_file_dir(clazz, src_filename, dst_filename, label):
    'Sync a dir.'
    try:
      os.mkdir(dst_filename)
    except OSError as ex:
      if ex.errno == errno.EEXIST:
        return
      else:
        print(("__sync_file_dir: caught: %s" % (ex)))
        raise
