#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check

class requirement_manager(object):

  def __init__(self):
    self._requirements = {}

check.register_class(requirement_manager, include_seq = False)
