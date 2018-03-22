#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

def rebuild_recipes(env):
  configure_env = [
    'all: CFLAGS=$REBUILD_REQUIREMENTS_CFLAGS LDFLAGS=$REBUILD_REQUIREMENTS_LDFLAGS PNG_COPTS=$REBUILD_REQUIREMENTS_CFLAGS',
  ]

  return env.args(
    properties = env.args(
      name = 'libpng',
      version = '1.6.18-1',
    ),
    requirements = [
 #     'all: zlib >= 1.2.8-1',
    ],
    steps = [
      'step_setup',
#      'step_setup_patch', { 'patches': [ 'all: reb-libpng-zlib.patch' ] },
      'step_autoconf_configure', { 'configure_env': configure_env },
      'step_make',
      'step_make_install',
      'step_cleanup',
      'step_artifact_create',
    ],
  )
