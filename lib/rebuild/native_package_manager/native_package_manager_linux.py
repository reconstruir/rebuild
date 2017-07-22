#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path as path
from native_package_manager_base import native_package_manager_base
from bes.common import Shell, string_util, string_list

class native_package_manager_linux(native_package_manager_base):

  def __init__(self):
    super(native_package_manager_linux, self).__init__()
    
  def installed_packages(self):
    'Return a list of installed pacakge.'
    cmd = 'dpkg -l'
    rv = self.__call_dpkg(cmd)
    if rv.exit_code != 0:
      raise RuntimeError('Failed to execute: %s' % (cmd))
    lines = rv.stdout.strip().split('\n')
    lines = [ l for l in lines if l.startswith('ii') ]
    lines = [ string_util.split_by_white_space(l)[1] for l in lines ]
    return sorted(lines)

  __CONTENTS_BLACKLIST = [
    '/.',
  ]
  def package_contents(self, package_name):
    'Return a list of installed pacakge.'
    cmd = 'dpkg-query -L %s' % (package_name)
    rv = self.__call_dpkg(cmd)
    if rv.exit_code != 0:
      raise RuntimeError('Failed to execute: %s' % (cmd))
    contents = rv.stdout.strip().split('\n')
    contents = string_list.remove_if(contents, self.__CONTENTS_BLACKLIST)
    return sorted(contents)

  def package_files(self, package_name):
    'Return a list of installed pacakge.'
    contents = self.package_contents(package_name)
    files = [ f for f in contents if path.isfile(f) ]
    return files

  def package_dirs(self, package_name):
    'Return a list of installed pacakge.'
    contents = self.package_contents(package_name)
    files = [ f for f in contents if path.isdir(f) ]
    return files

  def package_info(self, package_name):
    'Return a list of installed pacakge.'
    'apt-cache show bash'
    assert False

  def is_installed(self, package_name):
    'Return True if native_package_manager is installed.'
    cmd = 'dpkg -l %s' % (package_name)
    rv = self.__call_dpkg(cmd)
    return rv.exit_code == 0

  def owner(self, filename):
    'Return the package that owns filename.'
    cmd = 'dpkg -S %s' % (filename)
    rv = self.__call_dpkg(cmd)
    if rv.exit_code != 0:
      return None
    return rv.stdout.split(':')[0].strip()
  
  def __call_dpkg(self, cmd):
    'Call dpkg.'
    return Shell.execute(cmd, raise_error = False, shell = True)
