#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

def rebuild_recipes(env):

  def _foo(env):
    extra_tarballs = [
      'all: foo-extra-stuff',
    ]
    return env.args(
      properties = env.args(
        name = 'foo',
        version = '1.0.0',
      ),
      steps = [
        'step_setup', {
          'skip_unpack': True,
          'extra_tarballs': extra_tarballs,
        },
        'step_extract_tarballs_to_stage_dir',
        'step_post_install',
      ],
    )
  return [
    _foo,
  ]
