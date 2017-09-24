#!/usr/bin/env python
#-*- coding:utf-8 -*-

from abc import abstractmethod, ABCMeta

class _toolchain_base(object):

  __metaclass__ = ABCMeta

  @abstractmethod
  def compiler_environment(self, build_target):
    pass

  @abstractmethod
  def compiler_flags(clazz, build_target):
    pass
