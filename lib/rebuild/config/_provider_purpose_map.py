#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check
from bes.config import simple_config

class _provider_purpose_map(object):

  error = simple_config.error
  
  def __init__(self, label):
    check.check_string(label)
    self._label = label
    self._map = {}
    
  def get(self, purpose, provider):
    if not purpose in self._map or not provider in self._map[purpose]:
      raise self.error('No %s with purpose \"%s\" for provider \"%s\" found.' % (self._label, purpose, provider), None)
    return self._map[purpose][provider]

  def put(self, purpose, provider, what, origin):
    if not purpose in self._map:
      self._map[purpose] = {}
    if provider in self._map[purpose]:
      raise self.error('%s with purpose \"%s\" for provider \"%s\" already exists.' % (self._label, purpose, provider), origin)
    self._map[purpose][provider] = what
