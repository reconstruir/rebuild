#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.compat.plistlib import plistlib_loads
from bes.common.algorithm import algorithm
from bes.common.string_list_util import string_list_util
from bes.system.execute import execute

from .native_package_base import native_package_base
from .native_package_error import native_package_error
from .native_package_util import native_package_util

from .detail.pkgutil import pkgutil

class native_package_macos(native_package_base):

  def __init__(self):
    super(native_package_macos, self).__init__()
  
  #@abstractmethod
  def installed_packages(self):
    'Return a list of installed pacakge.'
    cmd = 'pkgutil --packages'
    rv = pkgutil.call_pkgutil('--packages')
    return native_package_util.parse_lines(rv.stdout, sort = True, unique = True)

  #@abstractmethod
  def package_manifest(self, package_name):
    'Return a list of installed files for the given package.'
    return self._package_manifest(package_name, '--only-files')

  #@abstractmethod
  def package_dirs(self, package_name):
    'Return a list of installed files for the given package.'
    return self._package_manifest(package_name, '--only-dirs')

  #@abstractmethod
  def package_contents(self, package_name):
    'Return a list of contents for the given package.'
    return self._package_manifest(package_name, None)

  _CONTENTS_BLACKLIST = [
    '.vol',
  ]

  def _package_manifest(clazz, package_name, flags):
    args = '--files {}'.format(package_name)
    if flags:
      args = args + ' ' + flags
    rv = pkgutil.call_pkgutil(args)
    files = native_package_util.parse_lines(rv.stdout, sort = True, unique = True)
    files = string_list_util.remove_if(files, clazz._CONTENTS_BLACKLIST)
    info = clazz.package_info(package_name)
    package_home = info['volume'] + info['install_location']
    package_home = package_home.replace('//', '/')
    return [ path.join(package_home, f) for f in files ]

  def _package_manifest(clazz, package_name, flags):
    args = '--files {}'.format(package_name)
    if flags:
      args = args + ' ' + flags
    rv = pkgutil.call_pkgutil(args)
    files = native_package_util.parse_lines(rv.stdout, sort = True, unique = True)
    files = string_list_util.remove_if(files, clazz._CONTENTS_BLACKLIST)
    info = clazz.package_info(package_name)
    package_home = info['volume'] + info['install_location']
    package_home = package_home.replace('//', '/')
    return [ path.join(package_home, f) for f in files ]
  
  #@abstractmethod
  def is_installed(self, package_name):
    'Return True if native_package is installed.'
    try:
      self.package_info(package_name)
    except native_package_error as ex:
      return False
    return True

  #@abstractmethod
  def owner(self, filename):
    'Return the package that owns filename.'
    args = '--file-info-plist {}'.format(filename)
    msg = 'Failed to get owner for filename: "{}"'.format(filename)
    rv = pkgutil.call_pkgutil(args, msg = msg)
    pi = plistlib_loads(rv.stdout.encode('utf-8')).get('path-info', None)
    if not pi:
      return None
    return pi[0].get('pkgid', None)
    
  #@abstractmethod
  def package_info(self, package_name):
    'Return platform specific information about a package.'
    args = '--pkg-info-plist {}'.format(package_name)
    msg = 'Failed to get info for package: "{}"'.format(package_name)
    rv = pkgutil.call_pkgutil(args, msg = msg)
    pi = plistlib_loads(rv.stdout.encode('utf-8'))
    return {
      'package_id': pi['pkgid'],
      'install_location': pi['install-location'],
      'volume': pi['volume'],
      'version': pi['pkg-version'],
    }

  #@abstractmethod
  def remove(self, package_name):
    'Remove a package.'
    if not self.is_installed(package_name):
      raise native_package_error('package not installed: "{}"'.format(package_name))
