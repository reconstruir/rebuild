#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import log
from bes.common import check

from .artifact_manager_registry import artifact_manager_registry

from collections import namedtuple

class artifact_manager_factory(object):

  config = namedtuple('config', 'local_cache_dir, sub_repo, no_network, storage_config')
  check.register_class(config, name = 'artifact_manager_factory_config')
  
  @classmethod
  def create(clazz, config):
    check.check_artifact_manager_factory_config(config)
    provider = config.storage_config.provider
    clazz.log_d('provider=%s; config=%s' % (provider, str(config)))
    clazz = artifact_manager_registry.get(provider)
    if not clazz:
      raise TypeError('Unknown provider type: \"%s\"' % (provider))
    return clazz(config)
    
  @classmethod
  def has_provider(clazz, provider):
    return artifact_manager_registry.get(provider) is not None

log.add_logging(artifact_manager_factory, 'artifact_manager_factory')
