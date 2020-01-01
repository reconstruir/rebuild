#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from rebuild.base.build_system import build_system

class ingest_cli_options(object):

  DEFAULT_CACHE_DIR = path.expanduser('~/.egoist/ingest/downloads')
  DEFAULT_SYSTEMS = [ build_system.HOST ]
  
  def __init__(self, *args, **kargs):
    self.verbose = False
    self.dry_run = False
    self.systems = self.DEFAULT_SYSTEMS
    self.cache_dir = self.DEFAULT_CACHE_DIR
    self.exclude = None
    self.include = None
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.verbose)
    check.check_bool(self.dry_run)
    check.check_string_seq(self.systems)
    check.check_string(self.cache_dir)
    check.check_string_seq(self.exclude, allow_none = True)
    check.check_string_seq(self.include, allow_none = True)

  def __str__(self):
    return str(self.__dict__)
    
check.register_class(ingest_cli_options)
