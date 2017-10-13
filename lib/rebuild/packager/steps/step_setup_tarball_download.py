#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import Step, step_result

class step_setup_tarball_download(Step):
  'Download a tarball.'

  def __init__(self):
    super(step_setup_tarball_download, self).__init__()

  def execute(self, argument):
    return step_result(True, None)

  def sources_keys(self):
    return [ 'downloaded_tarballs' ]

  @classmethod
  def parse_step_args(clazz, packager_env, args):
    result = {}
    pd = packager_env.package_descriptor
    tarball_address, tarball_revision = args.get('tarball_address', ( None, None ))
    if tarball_address:
      assert tarball_revision
      if not packager_env.downloads.has_tarball(tarball_address, tarball_revision):
        clazz.blurb('Downloading %s @ %s' % (tarball_address, tarball_revision))
      downloaded_path = packager_env.downloads.get_tarball(tarball_address, tarball_revision)
      result = { 'downloaded_tarballs': [ downloaded_path ] }
    return result
