#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.common import check, dict_util, string_util
from bes.config.simple_config import error, simple_config
from bes.fs import file_util

from .credentials_config import credentials_config
from ._provider_purpose_map import _provider_purpose_map

class storage_config(object):

  error = simple_config.error
  
  _storage = namedtuple('_storage', 'description, purpose, provider, credentials, root_dir, values, origin')
  
  def __init__(self, config, source, need_credentials = True):
    check.check_string(config)

    if need_credentials:
      credentials = credentials_config(config, source)
    else:
      credentials = None

    self._config = _provider_purpose_map('storage')

    c = simple_config.from_text(config, source = source)
    sections = c.find_sections('storage')
    for section in sections:
      values = section.to_dict(resolve_env_vars = True)
      description = section.find_by_key('description', raise_error = False)
      provider = section.find_by_key('provider')
      purpose = section.find_by_key('purpose', resolve_env_vars = True)
      purposes = credentials_config.parse_purposes(purpose)
      root_dir = section.find_by_key('root_dir', resolve_env_vars = True)
      dict_util.del_keys(values, [ 'description', 'provider', 'purpose', 'root_dir' ])
      for purpose in purposes:
        if need_credentials:
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
        
  @classmethod
  def from_file(clazz, filename, need_credentials = False):
    return clazz(file_util.read(filename), source = filename, need_credentials = need_credentials)

  @classmethod
  def from_text(clazz, text, source = None, need_credentials = False):
    return clazz(text, source = source, need_credentials = need_credentials)

  @classmethod
  def make_local_config(clazz, description, root_dir):
    description = description or 'auto generated default local build storage config.'
    check.check_string(description)
    check.check_string(root_dir)
    template = '''
credential
  provider: local
  purpose: download upload
#  username: 
#  password: 

storage
  description: {description}
  purpose: upload download
  provider: local
  root_dir: {root_dir}
'''
    content = template.format(description = description, root_dir = root_dir)
    return clazz.from_text(content, source = '<default>', need_credentials = False)
  
check.register_class(storage_config, include_seq = False)
  
