#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.common.check import check
from bes.system.log import logger
from bes.fs.file_resolve import file_resolve

from .ingest_file_parser import ingest_file_parser

class ingest_project(object):

  log = logger('ingest_project')
  
  def __init__(self, base_dir, args = []):
    self._resolved_files = file_resolve.resolve_mixed(base_dir, args, patterns = [ '*.reingest' ])
    self.log.log_d('resolved_files={}'.format(self._resolved_files))
    self._loaded_files = None
    self._entries = None
    
  def load(self):
    if self._loaded_files is not None:
      raise RuntimeError('Can only load once.')
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
#    for name, entry in self._entries.items():
#      print('{}: {}'.format(name, entry.origin))

  @property
  def files(self):
    return [ rf.filename for rf in self._resolved_files ]
      
  @property
  def files_abs(self):
    return [ rf.filename_abs for rf in self._resolved_files ]

  @property
  def entries(self):
    self._check_loaded()
    return sorted(self._entries.values())
  
  @property
  def entry_names(self):
    self._check_loaded()
    return sorted([ key for key in self._entries.keys() ])
  
  def find_entry(self, entry_name):
    self._check_loaded()
    if not self.has_entry(entry_name):
      raise KeyError('Entry not found: {}'.format(entry_name))
    return self._entries[entry_name]
  
  def has_entry(self, entry_name):
    self._check_loaded()
    return entry_name in self._entries
  
  def _check_loaded(self):
    if self._entries is None:
      raise RuntimeError('Need to call load() first.')
  
check.register_class(ingest_project, include_seq = False)
