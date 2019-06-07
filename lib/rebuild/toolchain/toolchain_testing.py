#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.host import host
from rebuild.base import build_arch, build_level, build_system, build_target
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
