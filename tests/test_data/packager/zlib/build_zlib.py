#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

def rebuild_recipes(env):
  configure_flags = [
    'all: --static',
  ]
  configure_env = [
    'all: CFLAGS=${REBUILD_COMPILE_CFLAGS}',
  ]
  return env.args(
    properties = env.args(
      name = 'zlib',
      version = '1.2.8',
      revision = '1',
    ),
    steps = [
      'step_autoconf', {
        'copy_source_to_build_dir': True,
        'configure_env': configure_env,
        'configure_flags': configure_flags,
      },
    ],
  )
