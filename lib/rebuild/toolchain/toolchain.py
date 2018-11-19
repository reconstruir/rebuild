#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import impl_import

from rebuild.base import build_system

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
    if build_target.system == build_system.ANDROID:
      #from ._toolchain_android import _toolchain_android
      from ._toolchain_android_standalone import _toolchain_android_standalone as _toolchain_android
      return _toolchain_android(build_target)
    elif build_target.system in [ build_system.IOS, build_system.IOS_SIM, build_system.MACOS ]:
      from ._toolchain_darwin import _toolchain_darwin
      return _toolchain_darwin(build_target)
    elif build_target.system == build_system.LINUX:
      from ._toolchain_linux import _toolchain_linux
      return _toolchain_linux(build_target)
    else:
      raise RuntimeError('Unknown build target: %s' % (build_target))
