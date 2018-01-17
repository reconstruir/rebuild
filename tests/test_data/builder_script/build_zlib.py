#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

def rebuild_recipes(env):
  return env.args(
    properties = env.args(
      name = 'zlib',
      version = '1.2.8-1',
      category = 'lib',
    ),
    steps = [
      'step_setup',
      'step_autoconf_configure',
      'step_make',
      'step_make_install',
      'step_cleanup',
      'step_artifact_create',
    ],
  )
