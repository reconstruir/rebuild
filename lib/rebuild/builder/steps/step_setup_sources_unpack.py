#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.archive import archiver

from rebuild.step import step, step_result

class step_setup_sources_unpack(step):
  'Prepare source tarballs..'

  def __init__(self):
    super(step_setup_sources_unpack, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    '''
  
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    downloaded_tarballs = inputs.get('downloaded_tarballs', None)
    if not downloaded_tarballs:
      return step_result(True, None)
      
    for t in downloaded_tarballs:
      self.blurb('Extracting %s to %s; base_dir=%s; strip_common_ancestor=%s' % (path.relpath(t.filename),
                                                                                 path.relpath(t.dest_dir),
                                                                                 t.base_dir,
                                                                                 t.strip_common_ancestor))
      archiver.extract(t.filename,
                       t.dest_dir,
                       base_dir = t.base_dir,
                       strip_common_ancestor = t.strip_common_ancestor)
      
    return step_result(True, None)
