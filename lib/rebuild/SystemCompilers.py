#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from build_target import System

class SystemCompilers(object):

  EXPECTED_VARIABLES = [ 'CC', 'CXX', 'RANLIB', 'AR', 'LIPO', 'APPLE_LIBTOOL', 'NM', 'LD' ]
  
  @classmethod
  def compilers_environment(clazz, build_target):
    'Return the compiler environment for the given system.'
    env = clazz.__system_specific_compilers_environment(build_target)
#    missing = clazz.__env_missing_variables(env)
#    if missing:
#      raise RuntimeError('Compilers environment is missing variables: %s' % (missing))
    return env

  @classmethod
  def compiler_flags(clazz, build_target):
    env = None
    if build_target.system in [ System.MACOS, System.IOS ]:
      from rebuild.darwin import SystemCompilersDarwin
      env = SystemCompilersDarwin.compiler_flags(build_target)
    elif build_target.system in [ System.LINUX ]:
      from rebuild.linux import SystemCompilersLinux
      env = SystemCompilersLinux.compiler_flags(build_target)
    else:
      raise RuntimeError('Unknown system: %s' % (system))

    more_env = {
#      'AR_WITH_FLAGS': '${AR} ${AR_FLAGS}',
#      'ARFLAGS': '${AR_FLAGS}',
    }

    env.update(more_env)

    return env
  
  @classmethod
  def __system_specific_compilers_environment(clazz, build_target):
    'Return the compiler environment for the given system.'
    env = None
    if build_target.system in [ System.MACOS, System.IOS ]:
      from rebuild.darwin import SystemCompilersDarwin
      env = SystemCompilersDarwin.compilers_environment(build_target)
    elif build_target.system in [ System.LINUX ]:
      from rebuild.linux import SystemCompilersLinux
      env = SystemCompilersLinux.compilers_environment(build_target)
    else:
      raise RuntimeError('Unknown system: %s' % (system))

    assert env
    
    more_env = {
#      'AR_WITH_FLAGS': '${AR} ${AR_FLAGS}',
#      'ARFLAGS': '${AR_FLAGS}',
    }

    env.update(more_env)

    return env
  
  @classmethod
  def __env_missing_variables(clazz, env):
    'Return True if the given env is has all the expected variables.'
    missing = []
    for v in clazz.EXPECTED_VARIABLES:
      if v not in env:
        missing.append(v)
    return missing

  @classmethod
  def __env_darwin(clazz):
    'Return the compiler environment for darwin.'
    return env

  @classmethod
  def flatten_for_shell(clazz, ce):
    'Return the compiler environment flattened and escaped for usage with shell commands.'
    def __item_to_string(key, value):
      # FIXME: shell escape
      return '%s=\"%s\"' % (key, value)
    v = [ __item_to_string(key, value) for key, value in ce.items() ]
    return ' '.join(v)
