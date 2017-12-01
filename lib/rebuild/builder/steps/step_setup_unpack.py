#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.archive import archiver
from rebuild.step import step, step_result
from rebuild.base import build_blurb
from bes.common import object_util, dict_util

class step_setup_unpack(step):
  'Unpack.'

  def __init__(self):
    super(step_setup_unpack, self).__init__()

  def execute(self, script, env, args):

    downloaded_tarballs = args.get('downloaded_tarballs', [])
    extra_tarballs = args.get('extra_tarballs', [])
    tarballs = args.get('tarballs', []) + extra_tarballs + downloaded_tarballs
    if not tarballs:
      return step_result(False, 'No tarballs found for %s.' % (script.descriptor.full_name))

    if args.get('skip_unpack', False):
      return step_result(True, None, output = { 'tarballs': tarballs })
    
    for tarball in tarballs:
      self.blurb('Extracting %s' % (tarball))
    self._extract(tarballs, script.working_dir, 'source', True)
    return step_result(True, None, output = { 'tarballs': tarballs })

  def sources_keys(self):
    return [ 'tarballs', 'extra_tarballs' ]

  @classmethod
  def parse_step_args(clazz, script, env, args):
    tarball_source_dir_override_args = clazz.resolve_step_args_dir(script, args, 'tarball_source_dir_override')
    if tarball_source_dir_override_args:
      tarball_source_dir_override = tarball_source_dir_override_args['tarball_source_dir_override']
      tmp_tarball_filename = '%s.tar.gz' % (script.descriptor.full_name)
      tmp_tarball_path = path.join(script.tmp_dir, tmp_tarball_filename)
      archiver.create(tmp_tarball_path, tarball_source_dir_override, base_dir = script.descriptor.full_name)
      tarballs_dict = { 'tarballs': [ tmp_tarball_path ] }
    else:
      tarballs_dict = clazz.resolve_step_args_list(script, args, 'tarballs')
    if not tarballs_dict or 'tarballs' not in tarballs_dict:
      tarball_name = args.get('tarball_name', None)
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
    extra_tarballs_dict = clazz.resolve_step_args_list(script, args, 'extra_tarballs')

    assert tarballs_dict
    assert isinstance(tarballs_dict, dict)
    assert 'tarballs' in tarballs_dict
    assert 'extra_tarballs' not in tarballs_dict

    if extra_tarballs_dict:
      assert isinstance(extra_tarballs_dict, dict)
      assert 'extra_tarballs' in extra_tarballs_dict
      assert 'tarballs' not in extra_tarballs_dict
      extra_tarballs = extra_tarballs_dict['extra_tarballs']
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
      archiver.extract(tarball,
                       dest_dir,
                       base_dir = base_dir,
                       strip_common_base = strip_common_base)
  