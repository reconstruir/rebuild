#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check

from bes.system import os_env_var
from bes.fs import file_find, file_path

class project_file_manager(object):

  def __init__(self):
    pass

  @classmethod
  def find_env_project_files(clazz):
    return file_path.glob(os_env_var('REBUILD_RECIPE_PATH').path, '*.reproject')
  
check.register_class(project_file_manager, include_seq = False)
