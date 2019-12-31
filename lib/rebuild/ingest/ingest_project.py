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

from .ingest_file_parser import ingest_file_parser

class ingest_project(object):

  log = logger('ingest_project')
  
  def __init__(self, base_dir, args = []):
    self._resolved_files = file_resolve.resolve_mixed(base_dir, args, patterns = [ '*.reingest' ])
    self._loaded_files = None
    
  def load(self):
    if self._loaded_files is not None:
      raise RuntimeError('can only load once.')
    self._loaded_files = {}
    for rf in self._resolved_files:
      pf = ingest_file_parser.parse_file(rf.filename_abs)
      assert rf.filename not in self._loaded_files
      self._loaded_files[rf.filename] = pf
    self._entries = {}
    for filename, pf in self._loaded_files.items():
      for entry in pf.entries:
        if entry.name in self._entries:
          raise RuntimeError('duplicate entry "{}" found:\n{}\n{}'.format(entry.name,
                                                                          self._entries[entry.name].origin,
                                                                          entry.origin))
        self._entries[entry.name] = entry
    for name, entry in self._entries.items():
      print('{}: {}'.format(name, entry.origin))

  @property
  def files(self):
    return [ rf.filename for rf in self._resolved_files ]
      
  @property
  def files_abs(self):
    return [ rf.filename_abs for rf in self._resolved_files ]
      
check.register_class(ingest_project, include_seq = False)
