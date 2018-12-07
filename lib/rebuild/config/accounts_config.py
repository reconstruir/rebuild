#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.common import check, dict_util
from bes.config.simple_config import error, simple_config
from bes.fs import file_util

from .credentials_config import credentials_config

class accounts_config(object):

  _config = namedtuple('_config', 'provider, credentials, origin')
  
  def __init__(self, config, source):
    check.check_string(config)

    cm = credentials_config(config, source)
    
    self._credentials = {}
    c = simple_config.from_text(config, source = source)
    
    sections = c.find_sections('artifacts')
    if len(sections) != 1:
      raise error('more that on artifacts section found', sections[1].origin)
    self.artifacts_upload, self.artifacts_download = self._make_config(sections[0], cm)

    sections = c.find_sections('sources')
    if len(sections) != 1:
      raise error('more that on sources section found', sections[1].origin)
    self.sources_upload, self.sources_download = self._make_config(sections[0], cm)

  @classmethod
  def _make_config(clazz, section, cm):
    provider = section.find_by_key('provider')
    values = section.to_dict()
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
  
