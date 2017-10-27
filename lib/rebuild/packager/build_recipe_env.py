#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from bes.system import host
from rebuild import build_type, System
from rebuild import variable_manager

class build_recipe_env(object):

  def __init__(self, build_target):
    self.build_target = build_target

    self.system = self.build_target.system
    self.build_type = self.build_target.build_type

    self.ANDROID = System.ANDROID
    self.IOS = System.IOS
    self.IOS_SIM = System.IOS_SIM
    self.LINUX = System.LINUX
    self.MACOS = System.MACOS

    self.DEBUG = build_type.DEBUG
    self.RELEASE = build_type.RELEASE

    self.DISTRO = host.DISTRO
    self.RASPBIAN = host.RASPBIAN
    self.UBUNTU = host.UBUNTU

  @classmethod
  def args(clazz, **kargs):
    return copy.deepcopy(kargs)

  @classmethod
  def simple_lib(clazz, name, version, revision, pkg_config_name, steps, **kargs):
    pkg_config_name = pkg_config_name or name
    args = clazz.args(
      properties = clazz.args(
        name = name,
        version = version,
        revision = revision,
        category = 'lib',
        pkg_config_name = pkg_config_name,
      ),
      steps = steps,
      **kargs)
    return lambda env: args

  @classmethod
  def add_variable(clazz, key, value):
    variable_manager.add_variable(key, value)

  def target_is_darwin(self):
    return self.build_target.is_darwin()

  def target_is_macos(self):
    return self.build_target.is_macos()

  def target_is_linux(self):
    return self.build_target.is_linux()
