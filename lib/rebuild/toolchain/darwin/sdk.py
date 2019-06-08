#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.base.build_system import build_system

class sdk(object):
  'Constants for xcode sdks and maps to convert with System constants.'
  MACOSX = 'macosx'
  IPHONE = 'iphoneos'
  IPHONE_SIMULATOR = 'iphonesimulator'

  VALID_SDKS = [ MACOSX, IPHONE, IPHONE_SIMULATOR ]

  SYSTEM_TO_SDK = {
    build_system.IOS: IPHONE,
    build_system.MACOS: MACOSX,
    build_system.IOS_SIM: IPHONE_SIMULATOR,
  }

  SDK_TO_SYSTEM = {
    IPHONE: build_system.IOS,
    MACOSX: build_system.MACOS,
    IPHONE_SIMULATOR: build_system.IOS_SIM,
  }

  @classmethod
  def is_valid_sdk(clazz, sdk):
    return sdk in clazz.VALID_SDKS
