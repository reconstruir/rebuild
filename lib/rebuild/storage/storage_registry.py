#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.factory.singleton_class_registry import singleton_class_registry

class storage_registry(singleton_class_registry):
  __registry_class_name_prefix__ = 'storage_'
  __registry_raise_on_existing__ = True
