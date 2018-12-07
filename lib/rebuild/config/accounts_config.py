#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.common import check, dict_util, string_util
from bes.config.simple_config import error, simple_config
from bes.fs import file_util

from .credentials_config import credentials_config

class accounts_config(object):

  error = simple_config.error
  
  _account = namedtuple('_account', 'name, description, purpose, provider, upload_values, download_values, origin')
  
  def __init__(self, config, source):
    check.check_string(config)
    credentials = credentials_config(config, source)

    self._accounts = {}
    c = simple_config.from_text(config, source = source)
    sections = c.find_sections('account')
    for section in sections:
      values = section.to_dict(resolve_env_vars = True)
      name = section.find_by_key('name')
      description = section.find_by_key('description', raise_error = False)
      provider = section.find_by_key('provider')
      purposes = string_util.split_by_white_space(section.find_by_key('purpose'), strip = True)
      del values['name']
      del values['purpose']
      del values['provider']
      if description is not None:
        del values['description']
      for purpose in purposes:
        if not purpose in self._accounts:
          self._accounts[purpose] = {}
        if name in self._accounts[purpose]:
          raise self.error('Account with purpose \"%s\" and name \"%s\" already exists.' % (purpose, name), section.origin)
        upload_values = dict_util.combine(values, credentials.find('upload', provider).values)
        download_values = dict_util.combine(values, credentials.find('download', provider).values)
        account = self._account(name, description, purpose, provider, upload_values, download_values, section.origin)
        self._accounts[purpose][name] = account

  def find(self, purpose, name):
    if not purpose in self._accounts or not name in self._accounts[purpose]:
      raise self.error('No account with purpose \"%s\" and name \"%s\" found.' % (purpose, name), None)
    return self._accounts[purpose][name]
        
  @classmethod
  def _make_account(clazz, section, cm):
    provider = section.find_by_key('provider')
    values = section.to_dict(resolve_env_vars = True)
    del values['provider']
    cred = cm.find('upload', provider)
    upload_config = clazz._config(provider, dict_util.combine(values, cred.values), section.origin)
    cred = cm.find('download', provider)
    download_config = clazz._config(provider, dict_util.combine(values, cred.values), section.origin)
    return upload_config, download_config
  
  @classmethod
  def from_file(clazz, filename):
    return clazz(file_util.read(filename), source = filename)
  
check.register_class(accounts_config, include_seq = False)
  
