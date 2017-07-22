#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.common import object_util

class dependency_provider(object):

  __metaclass__ = ABCMeta
  
  def __init__(self):
    pass
  
  @abstractmethod
  def provided(self):
    'Return a list of dependencies provided by this provider.'
    pass

  @classmethod
  def is_dependency_provider(clazz, o):
    return isinstance(o, dependency_provider)

  @classmethod
  def is_dependency_provider_list(clazz, l):
    return object_util.is_homogeneous(l, dependency_provider)

  @classmethod
  def determine_provided(clazz, o):
    'Determine the list of dependencies provided by o if it is a single or list of dependency provider(s).'
    if clazz.is_dependency_provider(o):
      return o.provided()
    elif clazz.is_dependency_provider_list(o):
      result = []
      for item in o:
        result.extend(item.provided())
      return result
    else:
      return []
