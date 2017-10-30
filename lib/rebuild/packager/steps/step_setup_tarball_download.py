#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import Step, step_result

class step_setup_tarball_download(Step):
  'Download a tarball.'

  def __init__(self):
    super(step_setup_tarball_download, self).__init__()

  def execute(self, script, env, args):
    return step_result(True, None)

  def sources_keys(self):
    return [ 'downloaded_tarballs' ]

  @classmethod
  def parse_step_args(clazz, script, args):
    result = {}
    tarball_address, tarball_revision = args.get('tarball_address', ( None, None ))
    if tarball_address:
      dm = script.env.downloads_manager
      assert tarball_revision
      if not dm.has_tarball(tarball_address, tarball_revision):
        tarball_path = dm.tarball_path(tarball_address, tarball_revision)
        clazz.blurb('Downloading %s@%s to %s' % (tarball_address, tarball_revision, tarball_path))
      downloaded_path = dm.get_tarball(tarball_address, tarball_revision)
      result = { 'downloaded_tarballs': [ downloaded_path ] }
    return result
