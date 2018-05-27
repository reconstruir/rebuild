#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import host
from rebuild.base import build_system, build_target
from .toolchain import toolchain

class toolchain_testing(object):

  @classmethod
  def can_compile_macos(clazz):
    return host.is_macos()

  @classmethod
  def can_compile_ios(clazz):
    return host.is_macos()

  @classmethod
  def android_toolchain_is_valid(clazz):
    return toolchain.get_toolchain(build_target(system = build_system.ANDROID)).is_valid()

  @classmethod
  def can_compile_android(clazz):
    return (host.is_macos() or host.is_linux()) and clazz.android_toolchain_is_valid()

  @classmethod
  def can_compile_linux(clazz):
    return host.is_linux()
