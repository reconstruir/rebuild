#!/usr/bin/env python
#-*- coding:utf-8 -*-

from native_package_manager_base import native_package_manager_base

import os.path as path
import plistlib
from bes.common import algorithm, Shell, string_list

class native_package_manager_macos(native_package_manager_base):

  def __init__(self):
    super(native_package_manager_macos, self).__init__()
    
  def installed_packages(self):
    'Return a list of installed pacakge.'
    cmd = 'pkgutil --packages'
    rv = self.__call_pkgutil(cmd)
    if rv.exit_code != 0:
      raise RuntimeError('Failed to execute: %s' % (cmd))
    return sorted(algorithm.unique(rv.stdout.strip().split('\n')))

  def package_files(self, package_name):
    'Return a list of installed files for the given package.'
    return self.__package_files(package_name, '--only-files')

  def package_dirs(self, package_name):
    'Return a list of installed files for the given package.'
    return self.__package_files(package_name, '--only-dirs')

  def package_contents(self, package_name):
    'Return a list of contents for the given package.'
    return self.__package_files(package_name, '')

  __CONTENTS_BLACKLIST = [
    '.vol',
  ]
  def __package_files(self, package_name, flags):
    cmd = 'pkgutil --files %s %s' % (package_name, flags)
    rv = self.__call_pkgutil(cmd)
    if rv.exit_code != 0:
      raise RuntimeError('Failed to execute: %s' % (cmd))
    files = sorted(algorithm.unique(rv.stdout.strip().split('\n')))
    files = string_list.remove_if(files, self.__CONTENTS_BLACKLIST)
    info = self.package_info(package_name)
    package_home = info['volume'] + info['install_location']
    package_home = package_home.replace('//', '/')
    return [ path.join(package_home, f) for f in files ]

  def is_installed(self, package_name):
    'Return True if native_package_manager is installed.'
    try:
      self.package_info(package_name)
    except RuntimeError, ex:
      return False
    return True

  def owner(self, filename):
    'Return the package that owns filename.'
    cmd = 'pkgutil --file-info-plist %s' % (filename)
    rv = self.__call_pkgutil(cmd)
    if rv.exit_code != 0:
      raise RuntimeError('Failed to get owner for package: %s' % (package_name))
    pi = plistlib.readPlistFromString(rv.stdout).get('path-info', None)
    if not pi:
      return None
    return pi[0].get('pkgid', None)
    
  def package_info(self, package_name):
    'Return True if native_package_manager is installed.'
    cmd = 'pkgutil --pkg-info-plist %s' % (package_name)
    rv = self.__call_pkgutil(cmd)
    if rv.exit_code != 0:
      raise RuntimeError('Failed to get info for package: %s' % (package_name))
    pi = plistlib.readPlistFromString(rv.stdout)
    return {
      'package_id': pi['pkgid'],
      'install_location': pi['install-location'],
      'volume': pi['volume'],
      'version': pi['pkg-version'],
    }

  def __call_pkgutil(self, cmd):
    'Return the output of pkgutil as lines.'
    return Shell.execute(cmd, raise_error = False)
