#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pkgutil
import os, os.path as path
from bes.common.algorithm import algorithm
from bes.system.check import check
from bes.common.object_util import object_util
from bes.common.string_util import string_util
from bes.system.execute import execute
from bes.system.log import logger
from bes.system.env_var import os_env_var
from bes.system.host import host
from bes.fs.file_find import file_find
from bes.fs.file_match import file_match
from bes.fs.file_path import file_path
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.python.package import package
from bes.build.build_arch import build_arch
from bes.build.build_blurb import build_blurb
from bes.build.build_system import build_system

class pkg_config(object):

  _LOG = logger('pkg_config')
  
  _PKG_CONFIG_VERSION = 'pkg-config-0.29.1'
  _PKG_CONFIG_SUB_PATH = path.join('pkg_config_binaries', host.SYSTEM, build_arch.HOST_ARCH, _PKG_CONFIG_VERSION)

  @classmethod
  def pkg_config_exe(clazz):
    if not hasattr(clazz, '_pkg_config_exe'):
      exe = clazz._find_exe()
      if not exe:
        raise RuntimeError('no pkgconf or pkg-config found in $PATH')
      setattr(clazz, '_pkg_config_exe', exe)
    return getattr(clazz, '_pkg_config_exe')

  _POSSIBLE_EXE = [
    'pkgconf',
    'pkg-config',
    'pykg-config.py',
  ]
  
  @classmethod
  def _find_exe(clazz):
    for possible_exe in clazz._POSSIBLE_EXE:
      exe = file_path.which(possible_exe, raise_error = False)
      if exe:
        return exe
    return None
  
  @classmethod
  def list_all(clazz, PKG_CONFIG_PATH = []):
    rv = clazz._call_pkg_config('--list-all',
                                PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    return clazz._parse_list_all_output(rv.stdout)

  @classmethod
  def cflags(clazz, modules, PKG_CONFIG_PATH = []):
    modules = object_util.listify(modules)
    args = [ '--cflags' ] + modules
    rv = clazz._call_pkg_config(args, PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    return clazz._parse_flags(rv.stdout)

  @classmethod
  def libs(clazz, modules, PKG_CONFIG_PATH = [], static = False):
    modules = object_util.listify(modules)
    args = [ '--libs' ] + modules
    if static:
      args.append('--static')
    rv = clazz._call_pkg_config(args, PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    libs = clazz._parse_flags(rv.stdout)
    libs = clazz._libs_cleanup(libs)
    return libs

  @classmethod
  def _libs_cleanup(clazz, libs):
    'Cleanups libs so that -ldl and -lpthread are last to work around bugs in some libs like openssl.'
    libs = libs[:]
    add_dl = False
    if '-ldl' in libs:
      libs.remove('-ldl')
      add_dl = True
    add_pthread = False
    if '-lpthread' in libs:
      libs.remove('-lpthread')
      add_pthread = True
    if add_dl:
      libs.append('-ldl')
    if add_pthread:
      libs.append('-lpthread')
    return libs

  # FIXME: add option for more path args
  @classmethod
  def make_pkg_config_path(clazz, root_dir):
    libdir = path.join(root_dir, 'lib/pkgconfig')
    sharedir = path.join(root_dir, 'share/pkgconfig')
    return [ libdir, sharedir ]

  @classmethod
  def make_pkg_config_path_for_unix_env(clazz, root_dir):
    return ':'.join(clazz.make_pkg_config_path(root_dir))

  @classmethod
  def find_pc_files(clazz, root_dir):
    pkg_config_path = clazz.make_pkg_config_path(root_dir)
    pc_files = []
    for p in pkg_config_path:
      if path.isdir(p):
        pc_files += file_find.find_fnmatch(p, [ '*.pc' ], file_match.ALL, relative = False)
    # Filter out symlinks
    return [ f for f in pc_files ]

  @classmethod
  def _parse_list_all_output(clazz, s):
    lines = [ line for line in s.split('\n') if line ]
    items = [ clazz._parse_list_all_entry(line) for line in lines ]
    assert None not in items
    return sorted(items, key = lambda item: item[0].lower())

  @classmethod
  def _parse_list_all_entry(clazz, s):
    i = s.find(' ')
    if i < 0:
      return None
    name = s[0:i]
    description = s[i:].strip()
    return ( name, description )

  @classmethod
  def _call_pkg_config(clazz, args, PKG_CONFIG_LIBDIR = [], PKG_CONFIG_PATH = []):
    check.check_string_seq(PKG_CONFIG_PATH)
    exe = clazz.pkg_config_exe()
    cmd = [ clazz.pkg_config_exe() ] + object_util.listify(args)
    env = {
      'PKG_CONFIG_DEBUG_SPEW': '1',
      'PKG_CONFIG_LIBDIR': ':'.join(PKG_CONFIG_LIBDIR),
      'PKG_CONFIG_PATH': ':'.join(PKG_CONFIG_PATH),
    }
    if exe.endswith('.py'):
      p = path.normpath(path.join(path.dirname(exe), path.pardir))
      python_lib_dir = path.join(p, 'lib', 'python')
      if path.isdir(python_lib_dir):
        env['PYTHONPATH'] = python_lib_dir
    #build_blurb.blurb_verbose('pkg_config', '_call_pkg_config() cmd=%s' % (str(cmd)))
    #print('pkg_config', '_call_pkg_config() cmd=%s; env=%s' % (str(cmd), str(env)))
    #print('pkg_config', '_call_pkg_config() cmd=%s' % (str(cmd)))
    rv = execute.execute(cmd, env = env)
    return rv
    
  @classmethod
  def _parse_flags(clazz, s):
    flags = string_util.split_by_white_space(s)
    return algorithm.unique([ flag.strip() for flag in flags ])
