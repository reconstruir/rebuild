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
    c = simple_config.from_text(config, source)
    sections = c.find_sections('credential')
    for section in sections:
      values = section.to_dict(resolve_env_vars = True)
      description = section.find_by_key('description', raise_error = False)
      provider = section.find_by_key('provider')
      cred_type = section.find_by_key('type')
      del values['type']
      del values['provider']
      if description is not None:
        del values['description']
      for next_cred_type in string_util.split_by_white_space(cred_type, strip = True):
        key = self._make_key(next_cred_type, provider)
        if not next_cred_type in self._credentials:
          self._credentials[next_cred_type] = {}
        if provider in self._credentials[next_cred_type]:
          raise self.error('Credential of type \"\%s\" for provider \"%s\" already exists.' % (next_cred_type, provider), section.origin)
        self._credentials[next_cred_type][provider] = self._credential(description, provider, next_cred_type, values, section.origin)
    
  def find(self, cred_type, provider):
    if not cred_type in self._credentials:
      raise self.error('No credential of type \"\%s\" for provider \"%s\" found.' % (next_cred_type, provider), section.origin)
    if not provider in self._credentials[cred_type]:
      raise self.error('No credential of type \"\%s\" for provider \"%s\" found.' % (next_cred_type, provider), section.origin)
    return self._credentials[cred_type][provider]

  def find_by_provider(self, provider):
    result = []
    for key, value in self._credentials.items():
      if value.provider == provider:
        result.append(value)
    return result
  
  @classmethod
  def _make_key(clazz, cred_type, provider):
    return '%s:%s' % (cred_type, provider)

check.register_class(credentials_config, include_seq = False)
  
