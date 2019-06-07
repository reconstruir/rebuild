#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.common.bool_util import bool_util
from bes.common.check import check
from bes.common.dict_util import dict_util
from bes.common.object_util import object_util
from bes.archive.archiver import archiver
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

from rebuild.step import step, step_result
from rebuild.base import build_blurb

class step_setup_sources_download(step):
  'Prepare source tarballs..'

  _downloaded_tarball = namedtuple('_downloaded_tarball', 'filename, dest_dir, base_dir, strip_common_ancestor')
    
  def __init__(self):
    super(step_setup_sources_download, self).__init__()

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
      return step_result(False, 'Only one of: tarball, tarball_address or tarball_dir can be given: %s' % (path.relpath(script.recipe.filename)))

    downloaded_tarballs = []
    outputs = {}
    
    if tarball_address:
      downloaded_path = tarball_address.downloaded_tarball_path(env.recipe_load_env)
      if tarball_address.needs_download(env.recipe_load_env):
        self.blurb('Downloading %s@%s to %s' % (tarball_address.address, tarball_address.revision, path.relpath(downloaded_path)))
        tarball_address.download(env.recipe_load_env)
      dest = tarball_address.get_property('dest', '${REBUILD_SOURCE_UNPACKED_DIR}')
      base_dir = tarball_address.get_property('base', None)
      strip_common_ancestor = tarball_address.get_property('strip_common_ancestor', True)
      downloaded_tarballs.append(self._downloaded_tarball(downloaded_path, dest, base_dir, strip_common_ancestor))

    if tarball:
      tarball_path = tarball.sources(env.recipe_load_env, script.substitutions)[0]
      if not tarball_path:
        blurb = 'No source (%s) found for %s using %s.' % (str(tarball.value),
                                                           script.descriptor.full_name,
                                                           str(env.sources_storage))
        self.blurb(blurb)
        possibilities = env.sources_storage.search(script.descriptor.name)
        if possibilities:
          self.blurb('Possible sources:')
          for p in possibilities:
            self.blurb('  %s' % (p))
        return step_result(False, blurb)
      dest = tarball.get_property('dest', '${REBUILD_SOURCE_UNPACKED_DIR}')
      base_dir = tarball.get_property('base', None)
      strip_common_ancestor = bool_util.parse_bool(tarball.get_property('strip_common_ancestor', 'True'))
      env.sources_storage.ensure_source(tarball_path)
      downloaded_tarballs.append(self._downloaded_tarball(tarball_path, dest, base_dir, strip_common_ancestor))
     
    if tarball_dir:
      tarball_dir.update(env.recipe_load_env)
      source_tarball = tarball_dir.sources(env.recipe_load_env, script.substitutions)[0]
      self.blurb('Creating tarball %s from %s' % (path.relpath(source_tarball), tarball_dir.value))
      tarball_path = tarball_dir.tarball()
      if not tarball_path:
        return step_result(False, 'No tarball found for %s' % (script.descriptor.full_name))
      dest = tarball_dir.get_property('dest', '${REBUILD_SOURCE_UNPACKED_DIR}')
      base_dir = tarball_dir.get_property('base', None)
      strip_common_ancestor = tarball_dir.get_property('strip_common_ancestor', True)
      downloaded_tarballs.append(self._downloaded_tarball(tarball_path, dest, base_dir, strip_common_ancestor))

    if env.config.download_only:
      outputs['_skip_rest'] = True
      return step_result(True, None, outputs = outputs)

    outputs['downloaded_tarballs'] = downloaded_tarballs
    return step_result(True, None, outputs = outputs)
