#!/usr/bin/env python
#-*- coding:utf-8 -*-

from .native_package_manager_base import native_package_manager_base

import os.path as path
from bes.compat.plistlib import plistlib_loads
from bes.common import algorithm, Shell, string_list_util

class native_package_manager_macos(native_package_manager_base):
    
  @classmethod
  def installed_packages(clazz):
    'Return a list of installed pacakge.'
    cmd = 'pkgutil --packages'
    rv = clazz._call_pkgutil(cmd)
    if rv.exit_code != 0:
      raise RuntimeError('Failed to execute: %s' % (cmd))
    return sorted(algorithm.unique(rv.stdout.strip().split('\n')))

  @classmethod
  def package_files(clazz, package_name):
    'Return a list of installed files for the given package.'
    return clazz.__package_files(package_name, '--only-files')

  @classmethod
  def package_dirs(clazz, package_name):
    'Return a list of installed files for the given package.'
    return clazz.__package_files(package_name, '--only-dirs')

  @classmethod
  def package_contents(clazz, package_name):
    'Return a list of contents for the given package.'
    return clazz.__package_files(package_name, '')

  __CONTENTS_BLACKLIST = [
    '.vol',
  ]

  @classmethod
  def __package_files(clazz, package_name, flags):
    cmd = 'pkgutil --files %s %s' % (package_name, flags)
    rv = clazz._call_pkgutil(cmd)
    if rv.exit_code != 0:
      raise RuntimeError('Failed to execute: %s' % (cmd))
    files = sorted(algorithm.unique(rv.stdout.strip().split('\n')))
    files = string_list_util.remove_if(files, clazz.__CONTENTS_BLACKLIST)
    info = clazz.package_info(package_name)
    package_home = info['volume'] + info['install_location']
    package_home = package_home.replace('//', '/')
    return [ path.join(package_home, f) for f in files ]

  @classmethod
  def is_installed(clazz, package_name):
    'Return True if native_package_manager is installed.'
    try:
      clazz.package_info(package_name)
    except RuntimeError as ex:
      return False
    return True

  @classmethod
  def owner(clazz, filename):
    'Return the package that owns filename.'
    cmd = 'pkgutil --file-info-plist %s' % (filename)
    rv = clazz._call_pkgutil(cmd)
    if rv.exit_code != 0:
      raise RuntimeError('Failed to get owner for package: %s' % (package_name))
    pi = plistlib_loads(rv.stdout.encode('utf-8')).get('path-info', None)
    if not pi:
      return None
    return pi[0].get('pkgid', None)
    
  @classmethod
  def package_info(clazz, package_name):
    'Return True if native_package_manager is installed.'
    cmd = 'pkgutil --pkg-info-plist %s' % (package_name)
    rv = clazz._call_pkgutil(cmd)
    if rv.exit_code != 0:
      raise RuntimeError('Failed to get info for package: %s' % (package_name))
    pi = plistlib_loads(rv.stdout.encode('utf-8'))
    return {
      'package_id': pi['pkgid'],
      'install_location': pi['install-location'],
      'volume': pi['volume'],
      'version': pi['pkg-version'],
    }

  @classmethod
  def _call_pkgutil(clazz, cmd):
    'Return the output of pkgutil as lines.'
    return Shell.execute(cmd, raise_error = False)
