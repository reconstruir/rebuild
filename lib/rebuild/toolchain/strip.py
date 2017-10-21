#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import impl_import

class strip(impl_import.load(__name__, '_strip', globals())):
  'Foo.'
  pass
