#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.common import check, object_util

class dependency_provider(with_metaclass(ABCMeta, object)):
  
  def __init__(self):
    pass
  
  @abstractmethod
  def provided(self):
    'Return a list of dependencies provided by this provider.'
    pass

  @classmethod
  def determine_provided(clazz, o):
    'Determine the list of dependencies provided by o if it is a single or list of dependency provider(s).'
    if check.is_dependency_provider(o):
      return o.provided()
    elif check.is_dependency_provider_seq(o):
      result = []
      for item in o:
        result.extend(item.provided())
      return result
    else:
      return []

check.register_class(dependency_provider)
