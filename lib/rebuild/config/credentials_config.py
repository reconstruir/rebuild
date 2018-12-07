#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from collections import namedtuple

from bes.common import check, string_util
from bes.config import simple_config

class credentials_config(object):

  error = simple_config.error
  
  _credential = namedtuple('_credential', 'description, provider, type, values, origin')
  
  def __init__(self, config, source):
    check.check_string(config)
    self._credentials = {}
    c = simple_config.from_text(config, source = source)
    sections = c.find_sections('credential')
    for section in sections:
      values = section.to_dict(resolve_env_vars = True)
      description = section.find_by_key('description', raise_error = False)
      provider = section.find_by_key('provider')
      purposes = string_util.split_by_white_space(section.find_by_key('purpose'), strip = True)
      del values['purpose']
      del values['provider']
      if description is not None:
        del values['description']
      for purpose in purposes:
        if not purpose in self._credentials:
          self._credentials[purpose] = {}
        if provider in self._credentials[purpose]:
          raise self.error('Credential with purpose \"%s\" for provider \"%s\" already exists.' % (purpose, provider), section.origin)
        credentials = self._credential(description, provider, purpose, values, section.origin)
        self._credentials[purpose][provider] = credentials
    
  def find(self, purpose, provider):
    if not purpose in self._credentials or not provider in self._credentials[purpose]:
      raise self.error('No credential with purpose \"%s\" for provider \"%s\" found.' % (purpose, provider), None)
    return self._credentials[purpose][provider]

  def find_by_provider(self, provider):
    result = []
    for key, value in self._credentials.items():
      if value.provider == provider:
        result.append(value)
    return result
  
check.register_class(credentials_config, include_seq = False)
  
