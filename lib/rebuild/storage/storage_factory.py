#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .storage_registry import storage_registry

from collections import namedtuple

class storage_factory(object):

  init_config = namedtuple('config', 'local_cache_dir, no_network, credentials')
  
  @classmethod
  def create(clazz, provider, config):
    clazz = storage_registry.get(provider)
    if not clazz:
      raise TypeError('Unknown provider type: \"%s\"' % (provider))
    return clazz(config)
    
  @classmethod
  def has_provider(clazz, provider):
    return storage_registry.get(provider) is not None
