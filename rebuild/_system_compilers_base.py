#!/usr/bin/env python
#-*- coding:utf-8 -*-

from abc import abstractmethod, ABCMeta

class _system_compilers_base(object):

  __metaclass__ = ABCMeta

  @abstractmethod
  def compilers_environment(self, build_target):
    pass

  @abstractmethod
  def compiler_flags(clazz, build_target):
    pass
