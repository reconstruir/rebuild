#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.common import check, string_util
from bes.config import simple_config

class credential_manager(object):

  _credential = namedtuple('_credential', 'type, provider, values, origin')
  
  def __init__(self, config):
    check.check_string(config)
    self._credentials = {}
    c = simple_config.from_text(config)
    sections = c.find_sections('credential')
    for section in sections:
      values = section.to_dict()
      provider = section.find_by_key('provider')
      cred_type = section.find_by_key('type')
      del values['type']
      del values['provider']
      for next_cred_type in string_util.split_by_white_space(cred_type, strip = True):
        key = self._make_key(next_cred_type, provider)
        self._credentials[key] = self._credential(next_cred_type, provider, values, section.origin)
    
  def find(self, cred_type, provider):
    key = self._make_key(cred_type, provider)
    return self._credentials.get(key, None)

  def find_by_provider(self, provider):
    result = []
    for key, value in self._credentials.items():
      if value.provider == provider:
        result.append(value)
    return result
  
  @classmethod
  def _make_key(clazz, cred_type, provider):
    return '%s:%s' % (cred_type, provider)
      
check.register_class(credential_manager, include_seq = False)
  
