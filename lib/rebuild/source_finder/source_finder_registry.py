#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.factory import singleton_class_registry

class source_finder_registry(singleton_class_registry):
  __registry_class_name_prefix__ = 'source_finder_'
  __registry_raise_on_existing__ = True
