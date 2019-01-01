#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.common import bool_util, check, dict_util, string_util
from bes.config.simple_config import error, simple_config
from bes.fs import file_util
from bes.config.simple_config import origin

from .new_storage_config import new_storage_config

class storage_config_manager(object):

  error = simple_config.error
  
  def __init__(self, config, source):
    check.check_string(config)
    check.check_string(source)
    self._configs = {}
    c = simple_config.from_text(config, source = source)
    sections = c.find_sections('storage')
    for section in sections:
      sc = new_storage_config.create_from_config(section)
      if sc.name in self._configs:
        raise self.error('storage with name \"%s\" already exists.', section.origin)
      self._configs[sc.name] = sc
      
  def get(self, name):
    return self._configs[name]

  @classmethod
  def from_file(clazz, filename):
    return storage_config_manager(file_util.read(filename), source = filename)

  @classmethod
  def from_text(clazz, text, source = None):
    return storage_config_manager(text, source = source)

  @classmethod
  def make_local_config(clazz, name, location, repo, root_dir):
    check.check_string(name)
    check.check_string(location)
    check.check_string(repo)
    check.check_string(root_dir)
    template = '''
storage
  name: {name}
  provider: local
  location: {location}
  repo: {repo}
  root_dir: {root_dir}
'''
    content = template.format(description = description, location = location, root_dir = root_dir)
    return clazz.from_text(content, source = '<default>')
  
check.register_class(storage_config_manager, include_seq = False)
  
