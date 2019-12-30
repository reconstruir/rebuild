#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

#from bes.compat.StringIO import StringIO
from bes.common.check import check
#from bes.common.node import node
#from bes.key_value.key_value_list import key_value_list
from bes.system.log import logger
from bes.fs.file_resolve import file_resolve

#from rebuild.recipe.recipe_error import recipe_error
#from rebuild.recipe.recipe_util import recipe_util

from .ingest_file import ingest_file

class ingest_project(object):

  log = logger('ingest_project')
  
  def __init__(self, base_dir, args = []):
    self._resolved_files = file_resolve.resolve_mixed(base_dir, args, patterns = [ '*.reingest' ])
    
  def load(self):
    pass

  @property
  def files(self):
    return [ rf.filename for rf in self._resolved_files ]
      
  @property
  def files_abs(self):
    return [ rf.filename_abs for rf in self._resolved_files ]
      
check.register_class(ingest_project, include_seq = False)
