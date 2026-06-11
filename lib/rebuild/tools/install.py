#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
from collections import namedtuple

from bes.files.bf_file_ops import bf_file_ops

class install(object):

  item = namedtuple('item', 'filename,dest_dir,mode')
  
  @classmethod
  def install(clazz, filename, dest_dir, mode = 0o755):
    bf_file_ops.mkdir(dest_dir)
    bf_file_ops.copy(filename, dest_dir)
    os.chmod(path.join(dest_dir, filename), mode)

  @classmethod
  def install_many(clazz, items):
    for item in items:
      clazz.install(item.filename, item.dest_dir, item.mode)
