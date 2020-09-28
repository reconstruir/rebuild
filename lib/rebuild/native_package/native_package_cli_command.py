#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os, pprint

from bes.common.Script import Script
from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.fs.file_path import file_path
from bes.script.blurber import blurber

from .native_package_error import native_package_error
from .native_package import native_package

class native_package_cli_command(object):
  'native_package cli commands.'

  @classmethod
  def handle_command(clazz, command, **kargs):
    kargs = copy.deepcopy(kargs)
    func = getattr(native_package_cli_command, command)
    bl = blurber(Script.name())
    verbose = kargs.pop('verbose')
    bl.set_verbose(verbose)
    np = native_package(bl)
    return func(np, **kargs)
  
  @classmethod
  def list(clazz, np):
    check.check_native_package(np)

    packages = np.installed_packages()
    for p in packages:
      print(p)
    return 0

  @classmethod
  def installed(clazz, np, package_name):
    check.check_native_package(np)
    check.check_string(package_name)

    if np.is_installed(package_name):
      return 0
    return 1

  @classmethod
  def info(clazz, np, package_name):
    check.check_native_package(np)
    check.check_string(package_name)

    info = np.package_info(package_name)
    print(pprint.pformat(info))
    return 0

  @classmethod
  def files(clazz, np, package_name, levels):
    check.check_native_package(np)
    check.check_string(package_name)

    files = np.package_files(package_name)
    if levels:
      files = [ clazz._level_path(p, levels) for p in files ]
      files = algorithm.unique(files)
    for f in files:
      print(f)
    return 0

  @classmethod
  def dirs(clazz, np, package_name, levels, root_dir):
    check.check_native_package(np)
    check.check_string(package_name)

    dirs = np.package_dirs(package_name)
    if levels:
      dirs = [ clazz._level_path(p, levels) for p in dirs ]
      dirs = algorithm.unique(dirs)
    if root_dir:
      ancestor = file_path.common_ancestor(dirs)
      if ancestor:
        print(ancestor)
    else:
      for f in dirs:
        print(f)
    return 0
  
  @classmethod
  def _level_path(clazz, p, levels):
    return os.sep.join(p.split(os.sep)[0 : levels])
  
  @classmethod
  def owner(clazz, np, filename):
    check.check_native_package(np)
    check.check_string(filename)

    owner = np.owner(filename)
    print(owner)
    return 0
  
  @classmethod
  def remove(clazz, np, package_name, force_package_root):
    check.check_native_package(np)
    check.check_string(package_name)
    check.check_bool(force_package_root)

    np.remove(package_name, force_package_root)
    return 0

  @classmethod
  def install(clazz, np, package_filename):
    check.check_native_package(np)
    check.check_string(package_filename)

    np.install(package_filename)
    return 0
  
