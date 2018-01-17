#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

def rebuild_recipes(env):
  configure_env = [
    'all: CFLAGS=${REBUILD_COMPILE_CFLAGS}',
  ]
  configure_flags = [
    'all: --enable-static --disable-shared',
    'linux: --with-pic',
  ]
  pc_files = [
#    'all: libjpeg.pc',
  ]    
  patches = [
#    'macos: reb-libjpeg-configure-ar.patch',
  ]
  return env.args(
    properties = env.args(
      name = 'libjpeg',
      version = '9a-1',
      category = 'lib',
    ),
    steps = [
      'step_autoconf', {
        'configure_env': configure_env,
        'configure_flags': configure_flags,
        'pc_files': pc_files,
        'patches': patches,
      }
    ],
  )
