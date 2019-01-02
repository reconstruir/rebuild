#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.config import storage_config_manager
from rebuild.package.artifact_manager_factory import artifact_manager_factory
from rebuild.package import artifact_manager_local

class artifact_manager_helper(object):

  @classmethod
  def make_local_artifact_manager(clazz, root_dir):
    scm = storage_config_manager.make_local_config('unit_test', root_dir, None, None)
    config = scm.get('unit_test')
    factory_config = artifact_manager_factory.config(None, None, True, config)
    return artifact_manager_local(factory_config)
