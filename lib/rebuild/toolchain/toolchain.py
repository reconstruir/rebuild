#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bes.system import impl_import

from rebuild import System

class toolchain(object):
  'Foo.'

  @classmethod
  def flatten_for_shell(clazz, ce):
    'Return the compiler environment flattened and escaped for usage with shell commands.'
    def _item_to_string(key, value):
      # FIXME: shell escape
      return '%s=\"%s\"' % (key, value)
    v = [ _item_to_string(key, value) for key, value in ce.items() ]
    return ' '.join(v)

  @classmethod
  def get_toolchain(clazz, build_target):
    'Return the toolchain for this particular build target.'
    if build_target.system == System.ANDROID:
      from ._toolchain_android import _toolchain_android
      return _toolchain_android(build_target)
    elif build_target.system in [ System.IOS, System.IOS_SIM, System.MACOS ]:
      from ._toolchain_darwin import _toolchain_darwin
      return _toolchain_darwin(build_target)
    elif build_target.system == System.LINUX:
      from ._toolchain_linux import _toolchain_linux
      return _toolchain_linux(build_target)
    else:
      raise RuntimeError('Unknown build target: %s' % (build_target))
