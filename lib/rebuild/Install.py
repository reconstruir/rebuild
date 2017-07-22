#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
from collections import namedtuple

from bes.fs import file_util

class Install(object):

  item = namedtuple('item', 'filename,dest_dir,mode')
  
  @classmethod
  def install(clazz, filename, dest_dir, mode = 0755):
    file_util.mkdir(dest_dir)
    file_util.copy(filename, dest_dir)
    os.chmod(path.join(dest_dir, filename), mode)

  @classmethod
  def install_many(clazz, items):
    for item in items:
      clazz.install(item.filename, item.dest_dir, item.mode)
