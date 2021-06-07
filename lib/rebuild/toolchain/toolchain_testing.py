#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.host import host
from bes.build.build_arch import build_arch
from bes.build.build_level import build_level
from bes.build.build_system import build_system
from bes.build.build_target import build_target
from .toolchain import toolchain

class toolchain_testing(object):

  @classmethod
  def can_compile_macos(clazz):
    return host.is_macos()

  @classmethod
  def can_compile_ios(clazz):
    return host.is_macos()

  BT = build_target(build_system.ANDROID, '', '', None, ( build_arch.ARMV7, ), build_level.RELEASE)
  @classmethod
  def android_toolchain_is_valid(clazz):
    return toolchain.get_toolchain(clazz.BT).is_valid()

  @classmethod
  def can_compile_android(clazz):
    return (host.is_macos() or host.is_linux()) and clazz.android_toolchain_is_valid()

  @classmethod
  def can_compile_linux(clazz):
    return host.is_linux()
