#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.common import check, dict_util, object_util
from bes.archive import archiver
from bes.fs import file_util, temp_file

from rebuild.step import step, step_result
from rebuild.base import build_blurb

class step_caca_source(step):
  'Prepare source tarballs..'

  def __init__(self):
    super(step_caca_source, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    tarball_dir              source_dir
    tarball_address          git_address
    tarball                  source_tarball
    '''
  
  def execute(self, script, env, args):
    values = self.values

    tarball_address = values['tarball_address']
    tarball_dir = values['tarball_dir']
    tarball = values['tarball']

    count = 0
    if tarball_address:
      count += 1
    if tarball_dir:
      count += 1
    if tarball:
      count += 1
    
    if count > 1:
      return step_result(False, 'Only one of: tarball, tarball_address or tarball_dir can be given.')
    
    if count > 0:
      setattr(script, 'fuck_no_tarballs', True)
      
    if tarball_address:
      tarball_address.substitutions = script.substitutions
      downloaded_path = tarball_address.downloaded_tarball_path()
      if tarball_address.needs_download():
        self.blurb('Downloading %s@%s to %s' % (tarball_address.address, tarball_address.revision, path.relpath(downloaded_path)))
        tarball_address.download()
      props = tarball_address.decode_properties()
      self.blurb('Extracting %s to %s' % (path.relpath(downloaded_path), path.relpath(props.dest)))
      archiver.extract(downloaded_path,
                       props.dest,
                       strip_common_base = props.strip_common_base)

    if tarball:
      tarball.substitutions = script.substitutions
      tarball_path = tarball.sources()[0]
      if not tarball_path:
        return step_result(False, 'No tarball found for %s' % (script.descriptor.full_name))
        
      props = tarball.decode_properties()
      self.blurb('Extracting %s to %s' % (path.relpath(tarball_path), path.relpath(props.dest)))
      archiver.extract(tarball_path,
                       props.dest,
                       strip_common_base = props.strip_common_base)
      
    if tarball_dir:
      tarball_dir.substitutions = script.substitutions
      tarball_path = tarball_dir.sources()[0]
      if not tarball_path:
        return step_result(False, 'No tarball found for %s' % (script.descriptor.full_name))
        
      props = tarball_dir.decode_properties()
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
    tarball_address = values['tarball_address']
    if tarball_address:
      result.extend(tarball_address.sources())
    return result

#  def sources_keys(self):
#    return [ 'tarballs', 'extra_tarballs' ]
