#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
from collections import namedtuple
from bes.common import object_util, Shell, string_util
from bes.fs import dir_util, file_util, temp_file

class Git(object):
  'A class to deal with git.'

  GIT_EXE = 'git'

  MODIFIED = 'M'
  ADDED = 'A'
  DELETED = 'D'
  RENAMED = 'R'
  COPIED = 'C'
  UNMERGED = 'U'
  UNKNOWN = '??'

  StatusItem = namedtuple('StatusItem', 'action, filename')
  
  @classmethod
  def status(clazz, root, filenames):
    filenames = object_util.listify(filenames)
    flags = [ '--porcelain' ]
    args = [ 'status' ] + flags + filenames
    rv = clazz.__call_git(root, args)
    return clazz.__parse_status_output(rv.stdout)

  @classmethod
  def has_changes(clazz, root):
    return clazz.status(root, '.') != []

  @classmethod
  def add(clazz, root, filenames):
    filenames = object_util.listify(filenames)
    flags = []
    args = [ 'add' ] + flags + filenames
    rv = clazz.__call_git(root, args)
    return rv

  @classmethod
  def move(clazz, root, src, dst):
    args = [ 'mv', src, dst ]
    rv = clazz.__call_git(root, args)
    return rv

  @classmethod
  def init(clazz, root):
    args = [ 'init', '.' ]
    rv = clazz.__call_git(root, args)
    return rv

  @classmethod
  def is_repo(clazz, root):
    expected_files = [ 'HEAD', 'config', 'index', 'refs', 'objects' ]
    for f in expected_files:
      if not path.exists(path.join(root, '.git', f)):
        return False
    return True

  @classmethod
  def __call_git(clazz, root, args):
    cmd = [ clazz.GIT_EXE ] + args
    #print "cmd: ", cmd
    return Shell.execute(cmd, cwd = root)

  @classmethod
  def __parse_status_output(clazz, s):
    lines = [ line.strip() for line in s.split('\n') ]
    lines = [ line for line in lines if line ]
    return [ clazz.__parse_status_line(line) for line in lines  ]

  @classmethod
  def __parse_status_line(clazz, s):
    v = string_util.split_by_white_space(s)
    assert len(v) == 2
    return clazz.StatusItem(v[0], v[1])

  @classmethod
  def clone(clazz, address, dest_dir, enforce_empty_dir = True):
    if path.exists(dest_dir):
      if not path.isdir(dest_dir):
        raise RuntimeError('dest_dir %s is not a directory.' % (dest_dir))
      if enforce_empty_dir:
        if not dir_util.is_empty(dest_dir):
          raise RuntimeError('dest_dir %s is not empty.' % (dest_dir))
    else:
      file_util.mkdir(dest_dir)
    args = [ 'clone', address, dest_dir ]
    clazz.__call_git(os.getcwd(), args)

  @classmethod
  def pull(clazz, root):
    args = [ 'pull', '--verbose' ]
    clazz.__call_git(root, args)

  @classmethod
  def commit(clazz, root, message, filenames):
    filenames = object_util.listify(filenames)
    message_filename = temp_file.make_temp_file(content = message)
    args = [ 'commit', '-F', message_filename ] + filenames
    clazz.__call_git(root, args)

  @classmethod
  def clone_or_update(clazz, address, dest_dir, enforce_empty_dir = True):
    if clazz.is_repo(dest_dir):
      if clazz.has_changes(dest_dir):
        raise RuntimeError('dest_dir %s has changes.' % (dest_dir))
      clazz.pull(dest_dir)
    else:
      clazz.clone(address, dest_dir, enforce_empty_dir = enforce_empty_dir)

  @classmethod
  def download_tarball(clazz, name, tag, address, archive_filename):
    'Download address to archive_filename.'
    archive_filename = path.abspath(archive_filename)
    tmp_dir = temp_file.make_temp_dir()
    clazz.clone(address, tmp_dir)
    flags = []
    args = [
      'archive',
      '--format=tgz',
      '--prefix=%s-%s/' % (name, tag),
      '-o',
      archive_filename,
      tag
    ]
    file_util.mkdir(path.dirname(archive_filename))
    rv = clazz.__call_git(tmp_dir, args)
    file_util.remove(tmp_dir)
