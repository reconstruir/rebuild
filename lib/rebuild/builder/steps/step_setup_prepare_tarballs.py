#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.common import bool_util, check, dict_util, object_util
from bes.archive import archiver
from bes.fs import file_util, temp_file

from rebuild.step import step, step_result
from rebuild.base import build_blurb

class step_setup_prepare_tarballs(step):
  'Prepare source tarballs..'

  _downloaded_tarball = namedtuple('_downloaded_tarball', 'filename, dest_dir, base_dir, strip_common_ancestor')
    
  def __init__(self):
    super(step_setup_prepare_tarballs, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    tarball_dir              source_dir
    tarball_address          git_address
    tarball                  source_tarball
    more_sources             file_list
    '''
  
  #@abstractmethod
  def execute(self, script, env, values, inputs):
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

    downloaded_tarballs = []
    
    if tarball_address:
      downloaded_path = tarball_address.downloaded_tarball_path()
      if tarball_address.needs_download():
        self.blurb('Downloading %s@%s to %s' % (tarball_address.address, tarball_address.revision, path.relpath(downloaded_path)))
        tarball_address.download()
      dest = tarball_address.get_property('dest', '${REBUILD_SOURCE_UNPACKED_DIR}')
      base_dir = tarball_address.get_property('base', None)
      strip_common_ancestor = tarball_address.get_property('strip_common_ancestor', True)
      downloaded_tarballs.append(self._downloaded_tarball(downloaded_path, dest, base_dir, strip_common_ancestor))

    if tarball:
      tarball_path = tarball.sources()[0]
      if not tarball_path:
        return step_result(False, 'No tarball found for %s' % (script.descriptor.full_name))
      dest = tarball.get_property('dest', '${REBUILD_SOURCE_UNPACKED_DIR}')
      base_dir = tarball.get_property('base', None)
      strip_common_ancestor = bool_util.parse_bool(tarball.get_property('strip_common_ancestor', 'True'))
      env.source_finder.ensure_source(tarball_path)
      downloaded_tarballs.append(self._downloaded_tarball(tarball_path, dest, base_dir, strip_common_ancestor))
     
    if tarball_dir:
      self.blurb('Creating tarball %s from %s' % (path.relpath(tarball_dir.sources()[0]), tarball_dir.where))
      tarball_path = tarball_dir.tarball()
      if not tarball_path:
        return step_result(False, 'No tarball found for %s' % (script.descriptor.full_name))
      dest = tarball_dir.get_property('dest', '${REBUILD_SOURCE_UNPACKED_DIR}')
      base_dir = tarball_dir.get_property('base', None)
      strip_common_ancestor = tarball_dir.get_property('strip_common_ancestor', True)
      downloaded_tarballs.append(self._downloaded_tarball(tarball_path, dest, base_dir, strip_common_ancestor))

    if env.config.download_only:
      return step_result(True, None, outputs = { '_skip_rest': True })

    outputs = { 'downloaded_tarballs': downloaded_tarballs }
    
    for tarball_path, dest, base_dir, strip_common_ancestor in downloaded_tarballs:
      self.blurb('Extracting %s to %s' % (path.relpath(tarball_path), path.relpath(dest)))
      archiver.extract(tarball_path,
                       dest,
                       base_dir = base_dir,
                       strip_common_ancestor = strip_common_ancestor)
      
    return step_result(True, None, outputs = outputs)
