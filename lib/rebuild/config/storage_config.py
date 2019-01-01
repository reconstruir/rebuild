#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.common import bool_util, check, dict_util, string_util
from bes.config.simple_config import error, simple_config
from bes.fs import file_util
from bes.config.simple_config import origin

from .credentials_config import credentials_config
from ._provider_purpose_map import _provider_purpose_map

class storage_config(object):

  error = simple_config.error
  
  _storage = namedtuple('_storage', 'description, purpose, provider, credentials, root_dir, values, origin')
  
  def __init__(self, config, source):
    check.check_string(config)

    credentials = None

    self._config = _provider_purpose_map('storage', origin(source, 1))

    c = simple_config.from_text(config, source = source)
    sections = c.find_sections('storage')
    for section in sections:
      values = section.to_dict(resolve_env_vars = True)
      description = section.find_by_key('description', raise_error = False)
      provider = section.find_by_key('provider')
      root_dir = section.find_by_key('root_dir', resolve_env_vars = True)
      no_credentials = section.find_by_key('no_credentials', raise_error = False) or 'false'
      no_credentials = bool_util.parse_bool(no_credentials)
      dict_util.del_keys(values, [ 'description', 'provider', 'root_dir', 'no_credentials' ])
      for purpose in [ 'download', 'upload' ]:
        if not no_credentials:
          if not credentials:
            credentials = credentials_config(config, source)
          cred = credentials.get(purpose, provider)
        else:
          cred = credentials_config._credential(None, provider, purpose, None, None, None)
        storage = self._storage(description,
                                purpose,
                                provider,
                                cred,
                                root_dir,
                                values,
                                section.origin)
        self._config.put(purpose, provider, storage, section.origin)

  def get(self, purpose, provider):
    return self._config.get(purpose, provider)

  def get_for_provider(self, provider):
    return self._config.get_for_provider(provider)

  def get_for_purpose(self, purpose):
    return self._config.get_for_purpose(purpose)
    
  @classmethod
  def from_file(clazz, filename):
    return clazz(file_util.read(filename), source = filename)

  @classmethod
  def from_text(clazz, text, source = None):
    return clazz(text, source = source)

  @classmethod
  def make_local_config(clazz, description, location, root_dir):
    content = clazz.make_local_config_content(description, location, root_dir)
    return clazz.from_text(content, source = '<default>')
  
  @classmethod
  def make_local_config_content(clazz, description, location, root_dir):
    description = description or 'auto generated default local build storage config.'
    check.check_string(description)
    check.check_string(location)
    check.check_string(root_dir)
    template = '''
credential
  provider: local
  purpose: download upload

storage
  description: {description}
  provider: local
  location: {location}
  root_dir: {root_dir}
  no_credentials: true
'''
    content = template.format(description = description, location = location, root_dir = root_dir)
    return content
  
check.register_class(storage_config, include_seq = False)
  
