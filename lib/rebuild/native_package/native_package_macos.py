#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import os

from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.common.string_list_util import string_list_util
from bes.compat.plistlib import plistlib_loads
from bes.fs.dir_util import dir_util
from bes.fs.file_mime import file_mime
from bes.fs.file_path import file_path
from bes.system.execute import execute

from bes.unix.sudo.sudo_exe import sudo_exe

from .native_package_base import native_package_base
from .native_package_error import native_package_error
from .native_package_util import native_package_util

from .detail.pkgutil import pkgutil

class native_package_macos(native_package_base):

  def __init__(self, blurber = None):
    super(native_package_macos, self).__init__(blurber)
  
  #@abstractmethod
  def installed_packages(self):
    'Return a list of installed pacakge.'
    cmd = 'pkgutil --packages'
    rv = pkgutil.call_pkgutil('--packages')
    return native_package_util.parse_lines(rv.stdout, sort = True, unique = True)

  #@abstractmethod
  def package_files(self, package_name):
    'Return a list of installed files for the given package.'
    return self._package_manifest(package_name, '--only-files')

  #@abstractmethod
  def package_dirs(self, package_name):
    'Return a list of installed files for the given package.'
    return self._package_manifest(package_name, '--only-dirs')

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
  def remove(self, package_name, force_package_root):
    'Remove a package.'
    check.check_string(package_name)
    check.check_bool(force_package_root)
    
    if not self.is_installed(package_name):
      raise native_package_error('package not installed: "{}"'.format(package_name))
    files = self.package_files(package_name)
    dirs = self.package_dirs(package_name)
    
    sudo_exe.validate(prompt = 'sudo password for remove:')
    for filename in files:
      if path.exists(filename):
        args = [ 'rm', '-f', filename ]
        sudo_exe.call_sudo(args)

    sorted_dirs = sorted(dirs, key = lambda d: d.count(os.sep), reverse = True)
    for dirname in sorted_dirs:
      if path.exists(dirname):
        if dir_util.is_empty(dirname):
          args = [ 'rmdir', dirname ]
          sudo_exe.call_sudo(args)
    
    if force_package_root:
      root_dir = file_path.common_ancestor(dirs)
      if root_dir and path.isdir(root_dir):
        if root_dir in [ '/', '/Applications', '/Library', '/bin', '/usr/bin', '/usr/local', '/opt' ]:
          raise native_package_error('Trying to delete a system directory: "{}"'.format(root_dir))
        args = [ 'rm', '-r', '-f', root_dir ]
        sudo_exe.call_sudo(args)

    args = [ '--forget', package_name ]
    pkgutil.call_pkgutil(args, use_sudo = True)

  #@abstractmethod
  def install(self, package_filename):
    'Install a package.'
    check.check_string(package_filename)

    if not path.isfile(package_filename):
      raise native_package_error('Package file not found: "{}"'.format(package_filename))

    mime_type = file_mime.mime_type(package_filename).mime_type
    if mime_type != 'application/x-xar':
      raise native_package_error('Invalid package file: "{}"'.format(package_filename))

    package_filename = path.abspath(package_filename)
    
    args = [ 'installer', '-verboseR', '-pkg', package_filename, '-target', '/' ]
    sudo_exe.call_sudo(args)
