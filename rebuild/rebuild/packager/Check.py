#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod

class Check(object):

  @abstractmethod
  def check(self, stage_dir, env):
    pass

class check_result(object):

  def __init__(self, success, message = None):
    self.success = success
    self.message = message

  def __str__(self):
    return '%s:%s' % (self.success, self.message)
