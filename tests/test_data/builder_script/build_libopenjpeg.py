#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

def rebuild_recipes(env):
  return env.args(
    properties = env.args(
      name = 'libopenjpeg',
      version = '2.1-1',
      category = 'lib',
    ),
    requirements = [ 
      #'all: cmake >= 3.3.1-1',
    ],
    steps = [
      'step_setup',
      'step_cmake_configure',
      'step_cmake_make',
      'step_cmake_install',
      'step_cleanup',
      'step_artifact_create',
    ],
  )
