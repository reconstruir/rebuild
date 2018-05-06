#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.common import check, dict_util, object_util
from bes.archive import archiver
from bes.fs import file_util, temp_file

from rebuild.step import step, step_result
from rebuild.base import build_blurb

class step_caca_source(step):
  'Unpack.'

  def __init__(self):
    super(step_caca_source, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
#    tarball                      file
#    extra_tarballs               string_list
#    tarball_name                 string
#    skip_unpack                  bool         False
#    tarball_source_dir_override  dir
#    tarball_override             file
    caca_source_dir               dir
    caca_tarball_address          git_address
    caca_tarball                  source
    '''
  
  def execute(self, script, env, args):
    values = self.values

    caca_tarball_address = values['caca_tarball_address']
    caca_tarball = values['caca_tarball']

    if caca_tarball_address and caca_tarball:
      return step_result(False, 'Only one caca_tarball_address and caca_tarball should be given.')
    
    if caca_tarball_address:
      caca_tarball_address.substitutions = script.substitutions
      downloaded_path = caca_tarball_address.downloaded_tarball_path()
      if caca_tarball_address.needs_download():
        self.blurb('Downloading %s@%s to %s' % (caca_tarball_address.address, caca_tarball_address.revision, path.relpath(downloaded_path)))
        caca_tarball_address.download()
      props = caca_tarball_address.decode_properties()
      self.blurb('Extracting %s to %s' % (path.relpath(downloaded_path), path.relpath(props.dest)))
      archiver.extract(downloaded_path,
                       props.dest,
                       strip_common_base = props.strip_common_base)

    if caca_tarball:
      caca_tarball.substitutions = script.substitutions
      tarball_path = caca_tarball.sources()[0]
      props = caca_tarball.decode_properties()
      self.blurb('Extracting %s to %s' % (path.relpath(tarball_path), path.relpath(props.dest)))
      archiver.extract(tarball_path,
                       props.dest,
                       strip_common_base = props.strip_common_base)
      
    return step_result(True, None)

  def sources(self, env):
    return self.tarballs(env)

  def tarballs(self, env):
    result = []
    values = self.values
    caca_tarball_address = values['caca_tarball_address']
    if caca_tarball_address:
      result.extend(caca_tarball_address.sources())
    return result

#  def sources_keys(self):
#    return [ 'tarballs', 'extra_tarballs' ]
