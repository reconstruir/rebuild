#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.common import bool_util, check, dict_util, object_util
from bes.archive import archiver
from bes.fs import file_util, temp_file

from rebuild.step import step, step_result
from rebuild.base import build_blurb
from rebuild.source_ingester import ingest_util

class step_ingest_upstream_sources(step):
  'Ingest upstream source tarballs and executable binaries.'

  def __init__(self):
    super(step_ingest_upstream_sources, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    upstream_source                source_tarball
    '''
  
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    upstream_source = values['upstream_source']

    if upstream_source:
      url = upstream_source.value
      arcname = upstream_source.get_property('arcname', None)
      checksum = upstream_source.get_property('checksum', None)
      remote_filename = upstream_source.get_property('remote_filename', None)
      if not remote_filename:
        return step_result(False, 'remote_filename needs to be given when ingesting a url.')
    
      if env.config.ingest:
        self.blurb('ingesting %s => %s [checksum %s]' % (url, remote_filename, checksum))
        rv = ingest_util.ingest_url(url, remote_filename, arcname, checksum, env.sources_storage)
        if not rv.success:
          return step_result(False, rv.reason)
        if rv.reason:
          self.blurb(rv.reason)
        env.sources_storage.reload_available()
      else:
        self.blurb('not ingesting %s (use --ingest to do)' % (url))
        
    if env.config.ingest_only:
      return step_result(True, None, outputs = { '_skip_rest': True })
      
    return step_result(True)
