#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.common.bool_util import bool_util
from bes.system.check import check
from bes.common.dict_util import dict_util
from bes.common.string_util import string_util
from bes.config.simple_config import simple_config
from bes.fs.file_util import file_util

from .storage_config import storage_config

class storage_config_manager(object):

  error = simple_config.error
  
  def __init__(self, config, source):
    check.check_string(source)
    self.source = source
    self._configs = {}

    if check.is_string(config):
      c = simple_config.from_text(config, source = source)
    elif check.is_node(config):
      c = simple_config.from_node(config, source = source)
    else:
      raise TypeError('Unknown config type: %s\nShould be string or node: %s - %s' % (source, str(config), type(config)))
    sections = c.find_all_sections('storage')
    for section in sections:
      sc = storage_config.create_from_config(source, section)
      if sc.name in self._configs:
        raise self.error('storage with name \"%s\" already exists.', section.origin)
      self._configs[sc.name] = sc
      
  def get(self, name):
    return self._configs.get(name, None)

  def available_configs(self):
    return sorted(self._configs.keys())
  
  @classmethod
  def from_file(clazz, filename):
    return storage_config_manager(file_util.read(filename, codec = 'utf8'), source = filename)

  @classmethod
  def from_text(clazz, text, source = None):
    return storage_config_manager(text, source = source)

  @classmethod
  def make_local_config(clazz, name, location, repo, root_dir):
    content = clazz.make_local_config_content(name, location, repo, root_dir)
    return clazz.from_text(content, source = '<default>')
  
  @classmethod
  def make_local_config_content(clazz, name, location, repo, root_dir):
    check.check_string(name)
    check.check_string(location)
    check.check_string(repo, allow_none = True)
    check.check_string(root_dir, allow_none = True)
    template = '''
storage
  name: {name}
  provider: local
  location: {location}
  repo: {repo}
  root_dir: {root_dir}
'''
    repo = repo or ''
    root_dir = root_dir or ''
    content = template.format(name = name, location = location, repo = repo, root_dir = root_dir)
    return content
  
check.register_class(storage_config_manager, include_seq = False)
