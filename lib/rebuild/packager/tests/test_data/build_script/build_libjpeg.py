#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from rebuild.packager import *

def rebuild_recipes(env):
  configure_flags = {
    env.LINUX: [ '--with-pic' ],
  }

  return env.args(
    properties = env.args(
      name = 'libjpeg',
      version = '9a-1',
      category = 'lib',
    ),
    steps = [
      step_setup,
      step_autoconf_configure, { 'configure_flags': configure_flags },
      step_shell, { 'cmd': 'make V=1' },
      step_shell, { 'cmd': 'make install prefix=$REBUILD_STAGE_PREFIX_DIR V=1' },
      step_pkg_config_make_pc, { 'pc_files': [ 'libjpeg.pc' ] },
      step_cleanup,
      step_artifact_create,
    ],
  )
