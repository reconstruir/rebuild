#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from rebuild.packager import *

def rebuild_recipes(env):
  configure_env = [
    'all: CFLAGS=$REBUILD_REQUIREMENTS_CFLAGS LDFLAGS=$REBUILD_REQUIREMENTS_LDFLAGS PNG_COPTS=$REBUILD_REQUIREMENTS_CFLAGS',
  ]

  return env.args(
    properties = env.args(
      name = 'libpng',
      version = '1.6.18-1',
      category = 'lib',
    ),
    requirements = [
      'all: zlib >= 1.2.8-1',
    ],
    steps = [
      step_setup,
      step_setup_patch, { 'patches': [ 'libpng-zlib.patch' ] },
      step_autoconf_configure, { 'configure_env': configure_env },
      step_make,
      step_make_install,
      step_cleanup,
      step_artifact_create,
    ],
  )

if __name__ == '__main__':
  Script.main(rebuild_recipes)
