#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from .native_package_base import native_package_base
from bes.common.string_util import string_util
from bes.common.string_list_util import string_list_util
from bes.system.execute import execute

# FIXME: this is ubuntu only
class native_package_linux(native_package_base):

  def __init__(self, blurber = None):
    super(native_package_linux, self).__init__(blurber)
  
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

  _CONTENTS_BLACKLIST = [
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
    contents = string_list_util.remove_if(contents, clazz._CONTENTS_BLACKLIST)
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
    'Return platform specific information about a package.'
    assert False

  @classmethod
  def is_installed(clazz, package_name):
    'Return True if native_package is installed.'
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
