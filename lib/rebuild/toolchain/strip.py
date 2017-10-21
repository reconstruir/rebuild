#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import impl_import
from rebuild import binary_detector

class strip(impl_import.load(__name__, '_strip', globals())):
  'Strip binaries.'

  @classmethod
  def check_strippable(clazz, binary):
    if not binary_detector.is_strippable(binary):
      raise RuntimeError('not a strippable binary: %s' % (binary))
