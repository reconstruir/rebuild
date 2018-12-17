#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import impl_import
from rebuild.binary_format import binary_detector

from bes.system import host
if host.SYSTEM == 'macos':
  from ._strip_macos import _strip_macos as _strip_super_class
elif host.SYSTEM == 'linux':
  from ._strip_linux import _strip_linux as _strip_super_class

#class strip(impl_import.load(__name__, '_strip', globals())):
class strip(_strip_super_class):
  'Strip binaries.'

  @classmethod
  def check_strippable(clazz, binary):
    if not binary_detector.is_strippable(binary):
      raise RuntimeError('not a strippable binary: %s' % (binary))
