#!/usr/bin/env python
#-*- coding:utf-8 -*-

from abc import abstractmethod, ABCMeta

class _strip_base(metaclass = ABCMeta):

  @abstractmethod
  def strip(self, build_target, binary):
    pass
