#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_util
from bes.python import package

class env_framework(object):

  _PACKAGE_PATH = 'shell_env_framework'
  
  _FILES = [
    'bin/bes_path.py',
    'env/bes_framework.sh',
    'env/bes_path.sh',
    'env/bes_testing.sh',
  ]
  
  def __init__(self):
    pass
  
  def extract(self, where):
    for f in self._FILES:
      src_path = path.join(self._PACKAGE_PATH, f)
      dst_path = path.join(where, f)
      content = package.get_data_content(src_path, __file__, __name__)
      file_util.save(dst_path, content = content, mode = 0o755)
