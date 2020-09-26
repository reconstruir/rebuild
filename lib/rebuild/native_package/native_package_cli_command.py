#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, pprint

from bes.common.algorithm import algorithm
from bes.common.check import check

from .native_package_error import native_package_error
from .native_package import native_package

class native_package_cli_command(object):
  'native_package cli commands.'

  @classmethod
  def handle_command(clazz, command, **kargs):
    func = getattr(native_package_cli_command, command)
    npm = native_package()
    return func(npm, **kargs)
  
  @classmethod
  def list(clazz, npm):
    check.check_native_package(npm)

    packages = npm.installed_packages()
    for p in packages:
      print(p)
    return 0

  @classmethod
  def installed(clazz, npm, package_name):
    check.check_native_package(npm)
    check.check_string(package_name)

    if npm.is_installed(package_name):
      return 0
    return 1

  @classmethod
  def info(clazz, npm, package_name):
    check.check_native_package(npm)
    check.check_string(package_name)

    info = npm.package_info(package_name)
    print(pprint.pformat(info))
    return 0

  @classmethod
  def contents(clazz, npm, package_name, levels, files_only, dirs_only):
    check.check_native_package(npm)
    check.check_string(package_name)

    if files_only and dirs_only:
      raise native_package_error('Only one of --files or --dirs can be given.')
    if files_only:
      files = npm.package_manifest(package_name)
    elif dirs_only:
      files = npm.package_dirs(package_name)
    else:
      files = npm.package_contents(package_name)
    if levels is not None:
      files = [ clazz._level_path(p, levels) for p in files ]
      files = algorithm.unique(files)
    for f in files:
      print(f)
    return 0
  
  @classmethod
  def _level_path(clazz, p, levels):
    return os.sep.join(p.split(os.sep)[0 : levels])
  
  @classmethod
  def owner(clazz, npm, filename):
    check.check_native_package(npm)
    check.check_string(filename)

    owner = npm.owner(filename)
    print(owner)
    return 0
