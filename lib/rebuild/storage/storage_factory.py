#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.log import log
from bes.system.check import check
from .storage_registry import storage_registry

from collections import namedtuple

class storage_factory(object):

  config = namedtuple('config', 'local_cache_dir, sub_repo, no_network, storage_config')
  check.register_class(config, name = 'storage_factory_config')
  
  @classmethod
  def create(clazz, config):
    provider = config.storage_config.provider
    clazz.log_i('provider=%s; config=%s' % (provider, str(config)))
    clazz = storage_registry.get(provider)
    if not clazz:
      raise TypeError('Unknown provider type: \"%s\"' % (provider))
    return clazz(config)
    
  @classmethod
  def has_provider(clazz, provider):
    return storage_registry.get(provider) is not None

log.add_logging(storage_factory, 'storage_factory')
