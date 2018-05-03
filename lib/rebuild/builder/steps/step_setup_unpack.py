#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.common import check, dict_util, object_util
from bes.archive import archiver
from bes.fs import file_util, temp_file

from rebuild.step import step, step_result
from rebuild.base import build_blurb

class step_setup_unpack(step):
  'Unpack.'

  def __init__(self):
    super(step_setup_unpack, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    no_tarballs                  bool         False
    extra_tarballs               string_list
    tarball_name                 string
    skip_unpack                  bool         False
    tarball_source_dir_override  dir
    tarball_override             file
    '''

  def execute(self, script, env, args):
    no_tarballs = self.values.get('no_tarballs')
    tarball_name = self.values.get('tarball_name')
    skip_unpack = self.values.get('skip_unpack')
      
    if no_tarballs:
      return step_result(True, None)

    extra_tarballs = args.get('extra_tarballs', None)

    if check.is_string_list(extra_tarballs):
      extra_tarballs = extra_tarballs.to_list()
    else:
      if extra_tarballs:
        check.check_list(extra_tarballs)
      else:
        extra_tarballs = []

    downloaded_tarballs = args.get('downloaded_tarballs', [])
    tarballs = args.get('tarballs', []) + extra_tarballs + downloaded_tarballs
    if not tarballs:
      #tarball_name = args.get('tarball_name', None)
      blurb = 'No tarballs found for %s' % (script.descriptor.full_name)
      if tarball_name:
        blurb = '%s (tarball_name=\"%s\")' % (blurb, tarball_name)
      return step_result(False, '%s.' % (blurb))

    if args.get('skip_unpack', False):
      return step_result(True, None, output = { 'tarballs': tarballs })
    
    self._extract(tarballs, script.working_dir, 'source', True)
    
    return step_result(True, None, output = { 'tarballs': tarballs })

  def sources_keys(self):
    return [ 'tarballs', 'extra_tarballs' ]

  @classmethod
  def parse_step_args(clazz, script, env, values):
    tarball_name = values.get('tarball_name')
    tarball_source_dir_override = values.get('tarball_source_dir_override')
    tarball_override = values.get('tarball_override')
    if tarball_source_dir_override:
      tarball_source_dir_override = tarball_source_dir_override.filename
    extra_tarballs = values.get('extra_tarballs')

    if check.is_string_list(extra_tarballs):
      extra_tarballs = extra_tarballs.to_list()
    else:
      if extra_tarballs:
        check.check_list(extra_tarballs)

    if tarball_override:
      tarballs_dict = { 'tarballs': [ tarball_override.filename ] }
    elif tarball_source_dir_override:
      tmp_dir = temp_file.make_temp_dir(delete = False)
      tmp_tarball_filename = '%s.tar.gz' % (script.descriptor.full_name)
      tmp_tarball_path = path.join(tmp_dir, tmp_tarball_filename)
      archiver.create(tmp_tarball_path, tarball_source_dir_override, base_dir = script.descriptor.full_name)
      assert path.isfile(tmp_tarball_path)
      tarballs_dict = { 'tarballs': [ tmp_tarball_path ] }
    else:
      tarballs_dict = {}
    if not tarballs_dict or 'tarballs' not in tarballs_dict:
      if tarball_name:
        clazz.blurb_verbose('Using tarball name \"%s\" instead of \"%s\" for %s' % (tarball_name, script.descriptor.name, script.descriptor.full_name))
      else:
        tarball_name = script.descriptor.name

      tarball = env.source_finder.find_source(tarball_name,
                                              script.descriptor.version.upstream_version,
                                              script.build_target.system)
      if tarball:
        tarballs_dict = { 'tarballs': [ tarball ] }
      else:
        tarballs_dict = { 'tarballs': [] }

    assert tarballs_dict
    assert isinstance(tarballs_dict, dict)
    assert 'tarballs' in tarballs_dict

    extra_tarballs_dict = {}
    if extra_tarballs:
      extra_tarballs_result = []
      for extra_tarball in extra_tarballs:
        tp = env.source_finder.find_source(extra_tarball, '', script.build_target.system)
        if not tp:
          raise RuntimeError('%s: Failed to find extra tarball: %s' % (script.descriptor.full_name, extra_tarball))
        extra_tarballs_result.append(tp)
      extra_tarballs_dict['extra_tarballs'] = extra_tarballs_result

    return dict_util.combine(tarballs_dict, extra_tarballs_dict)

  @classmethod
  def _extract(clazz, tarballs, dest_dir, base_dir, strip_common_base):
    tarballs = object_util.listify(tarballs)
    for tarball in tarballs:
      clazz.blurb('Extracting source tarballs %s to %s' % (path.relpath(tarball), path.relpath(dest_dir)))
      archiver.extract(tarball,
                       dest_dir,
                       base_dir = base_dir,
                       strip_common_base = strip_common_base)
  
