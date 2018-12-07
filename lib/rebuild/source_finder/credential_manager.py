#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.common import check
from bes.config import simple_config

class credential_manager(object):

  _credential = namedtuple('_credential', 'type, provider, values, origin')
  
  def __init__(self, config):
    check.check_string(config)
    self._credentials = {}
    c = simple_config.from_text(config)
    sections = c.find_sections('credential')
    for section in sections:
      d = section.to_dict()
      cred_type = section.find_by_key('type')
      provider = section.find_by_key('provider')
      values = section.to_dict()
      del values['type']
      del values['provider']
      key = self._make_key(cred_type, provider)
      self._credentials[key] = self._credential(cred_type, provider, values, section.origin)
    
  def find(self, cred_type, provider):
    key = self._make_key(cred_type, provider)
    return self._credentials.get(key, None)

  @classmethod
  def _make_key(clazz, cred_type, provider):
    return '%s:%s' % (cred_type, provider)
      
check.register_class(credential_manager, include_seq = False)
  