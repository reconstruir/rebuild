#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bes.system import impl_import

class toolchain(impl_import.load('_toolchain', globals())):
  'Foo.'

  @classmethod
  def flatten_for_shell(clazz, ce):
    'Return the compiler environment flattened and escaped for usage with shell commands.'
    def __item_to_string(key, value):
      # FIXME: shell escape
      return '%s=\"%s\"' % (key, value)
    v = [ __item_to_string(key, value) for key, value in ce.items() ]
    return ' '.join(v)

