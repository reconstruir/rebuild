#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import algorithm, object_util, Shell, string_util
from bes.system import log, os_env_var, host
from bes.fs import file_find, file_match
from rebuild import build_blurb, build_arch, System

class pkg_config(object):

  # FIXME: maybe this should be centralized
  def __pkg_config_exe():
    version = '0.29.1'
    exe = 'rebbe_pkg-config'
    tools_root = path.normpath(path.join(path.dirname(__file__), '..', 'tools', host.SYSTEM, build_arch.HOST_ARCH))
    return path.join(tools_root, 'pkg_config-%s_rev1' % (version), 'bin', exe)

  PKG_CONFIG_EXE = __pkg_config_exe()

  @classmethod
  def list_all(clazz, PKG_CONFIG_PATH = []):
    rv = clazz.__call_pkg_config('--list-all',
                                 PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    return clazz.__parse_list_all_output(rv.stdout)

  @classmethod
  def cflags(clazz, modules, PKG_CONFIG_PATH = []):
    modules = object_util.listify(modules)
    args = [ '--cflags' ] + modules
    rv = clazz.__call_pkg_config(args, PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    return clazz.__parse_flags(rv.stdout)

  @classmethod
  def libs(clazz, modules, PKG_CONFIG_PATH = [], static = False):
    modules = object_util.listify(modules)
    args = [ '--libs' ] + modules
    if static:
      args.append('--static')
    rv = clazz.__call_pkg_config(args, PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    libs = clazz.__parse_flags(rv.stdout)
    libs = clazz.__libs_cleanup(libs)
    return libs

  @classmethod
  def __libs_cleanup(clazz, libs):
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

  @classmethod
  def __make_lib_pkgconfig_dir(clazz, root_dir):
    return path.join(root_dir, 'lib/pkgconfig')

  @classmethod
  def __make_share_pkgconfig_dir(clazz, root_dir):
    return path.join(root_dir, 'share/pkgconfig')

  # FIXME: add option for more path args
  @classmethod
  def make_pkg_config_path(clazz, root_dir):
    libdir = clazz.__make_lib_pkgconfig_dir(root_dir)
    sharedir = clazz.__make_share_pkgconfig_dir(root_dir)
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
  def __parse_list_all_output(clazz, s):
    lines = [ line for line in s.split('\n') if line ]
    items = [ clazz.__parse_list_all_entry(line) for line in lines ]
    assert None not in items
    return sorted(items, key = lambda item: item[0].lower())

  @classmethod
  def __parse_list_all_entry(clazz, s):
    i = s.find(' ')
    if i < 0:
      return None
    name = s[0:i]
    description = s[i:].strip()
    return ( name, description )

  @classmethod
  def __call_pkg_config(clazz, args, PKG_CONFIG_LIBDIR = [], PKG_CONFIG_PATH = []):
    cmd = [ clazz.PKG_CONFIG_EXE ] + object_util.listify(args)
    env = {
      'PKG_CONFIG_LIBDIR': ':'.join(PKG_CONFIG_LIBDIR),
      'PKG_CONFIG_PATH': ':'.join(PKG_CONFIG_PATH),
      'PATH': os_env_var('PATH').value,
    }
    #build_blurb.blurb_verbose('pkg_config', '__call_pkg_config() cmd=%s' % (str(cmd)))
    #print('pkg_config', '__call_pkg_config() cmd=%s' % (str(cmd)))
    rv = Shell.execute(cmd, env = env)
    #build_blurb.blurb_verbose('pkg_config', '__call_pkg_config() rv=%s' % (str(rv)))
    #print('pkg_config', '__call_pkg_config() rv=%s' % (str(rv)))
    return rv
    
  @classmethod
  def __parse_flags(clazz, s):
    flags = string_util.split_by_white_space(s)
    return algorithm.unique([ flag.strip() for flag in flags ])

log.add_logging(pkg_config, 'pkg_config')
