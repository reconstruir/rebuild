#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from collections import namedtuple

from bes.common import check, dict_util, string_util
from bes.config import simple_config

from ._provider_purpose_map import _provider_purpose_map
from bes.config.simple_config import origin

class credentials_config(object):

  error = simple_config.error
  
  _credential = namedtuple('_credential', 'description, provider, purpose, username, password, origin')
  
  def __init__(self, config, source):
    check.check_string(config)
    self._credentials = _provider_purpose_map('credential', origin(source, 1))
    c = simple_config.from_text(config, source = source)
    sections = c.find_sections('credential')
    for section in sections:
      description = section.find_by_key('description', raise_error = False, resolve_env_vars = True)
      provider = section.find_by_key('provider', resolve_env_vars = True)
      purpose = section.find_by_key('purpose', resolve_env_vars = True)
      purposes = self.parse_purposes(purpose)
      username = section.find_by_key('username', resolve_env_vars = True)
      password = section.find_by_key('password', resolve_env_vars = True)
      values = section.to_dict(resolve_env_vars = True)
      dict_util.del_keys(values, [ 'purpose', 'provider', 'description', 'username', 'password' ])
      invalid_keys = values.keys()
      if invalid_keys:
        raise self.error('Invalid setting(s): %s' % (' '.join(invalid_keys)), section.origin)
      for purpose in purposes:
        credentials = self._credential(description, provider, purpose, username, password, section.origin)
        self._credentials.put(purpose, provider, credentials, section.origin)
    
  def get(self, purpose, provider):
    return self._credentials.get(purpose, provider)

  @classmethod
  def parse_purposes(clazz, s):
    return string_util.split_by_white_space(s, strip = True)
  
check.register_class(credentials_config, include_seq = False)
  
