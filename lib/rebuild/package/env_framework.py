#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_util
from bes.python import package

class env_framework(object):

  _PACKAGE_PATH = 'shell_env_framework'
  
  _FILES = [
    'env/bes_framework.sh',
  ]
  
  def __init__(self):
    pass
  
  def extract(self, where):
    for f in self._FILES:
      src_path = path.join(self._PACKAGE_PATH, f)
      dst_path = path.join(where, f)
      content = package.get_data_content(src_path, __file__, __name__)
      if not content:
        raise RuntimeError('Failed to get package data: %s' % (src_path))
      file_util.save(dst_path, content = content, mode = 0o755)
      if file_util.read(dst_path) != content:
        raise RuntimeError('Failed to save %s.' % (dst_path))
