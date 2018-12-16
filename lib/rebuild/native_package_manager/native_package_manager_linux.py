#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path as path
from .native_package_manager_base import native_package_manager_base
from bes.common import string_util, string_list_util
from bes.system import execute

class native_package_manager_linux(native_package_manager_base):

  @classmethod
  def installed_packages(clazz):
    'Return a list of installed pacakge.'
    cmd = 'dpkg -l'
    rv = clazz._call_dpkg(cmd)
    if rv.exit_code != 0:
      raise RuntimeError('Failed to execute: %s' % (cmd))
    lines = rv.stdout.strip().split('\n')
    lines = [ l for l in lines if l.startswith('ii') ]
    lines = [ string_util.split_by_white_space(l)[1] for l in lines ]
    return sorted(lines)

  __CONTENTS_BLACKLIST = [
    '/.',
  ]

  @classmethod
  def package_contents(clazz, package_name):
    'Return a list of installed pacakge.'
    cmd = 'dpkg-query -L %s' % (package_name)
    rv = clazz._call_dpkg(cmd)
    if rv.exit_code != 0:
      raise RuntimeError('Failed to execute: %s' % (cmd))
    contents = rv.stdout.strip().split('\n')
    contents = string_list_util.remove_if(contents, clazz.__CONTENTS_BLACKLIST)
    return sorted(contents)

  @classmethod
  def package_manifest(clazz, package_name):
    'Return a list of installed pacakge.'
    contents = clazz.package_contents(package_name)
    files = [ f for f in contents if path.isfile(f) ]
    return files

  @classmethod
  def package_dirs(clazz, package_name):
    'Return a list of installed pacakge.'
    contents = clazz.package_contents(package_name)
    files = [ f for f in contents if path.isdir(f) ]
    return files

  @classmethod
  def package_info(clazz, package_name):
    'Return a list of installed pacakge.'
    'apt-cache show bash'
    assert False

  @classmethod
  def is_installed(clazz, package_name):
    'Return True if native_package_manager is installed.'
    cmd = 'dpkg -l %s' % (package_name)
    rv = clazz._call_dpkg(cmd)
    return rv.exit_code == 0

  @classmethod
  def owner(clazz, filename):
    'Return the package that owns filename.'
    cmd = 'dpkg -S %s' % (filename)
    rv = clazz._call_dpkg(cmd)
    if rv.exit_code != 0:
      return None
    return rv.stdout.split(':')[0].strip()
  
  @classmethod
  def _call_dpkg(clazz, cmd):
    'Call dpkg.'
    return execute.execute(cmd, raise_error = False, shell = True)
