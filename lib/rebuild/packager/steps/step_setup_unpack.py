#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.archive import archiver
from rebuild.step_manager import Step, step_result
from rebuild import build_blurb, TarballUtil
from bes.common import object_util, dict_util
from bes.fs import file_util

class step_setup_unpack(Step):
  'Unpack.'

  def __init__(self):
    super(step_setup_unpack, self).__init__()

  def execute(self, argument):
    downloaded_tarballs = argument.args.get('downloaded_tarballs', [])
    extra_tarballs = argument.args.get('extra_tarballs', [])
    tarballs = argument.args.get('tarballs', []) + extra_tarballs + downloaded_tarballs
    if not tarballs:
      return step_result(False, 'No tarballs found.')
      
    for tarball in tarballs:
      self.blurb('Extracting %s' % (tarball))
    TarballUtil.extract(tarballs, argument.env.working_dir, 'source', True)
    return step_result(True, None)

  def sources_keys(self):
    return [ 'tarballs', 'extra_tarballs' ]

  @classmethod
  def parse_step_args(clazz, packager_env, args):
    tarball_source_dir_override_args = clazz.resolve_step_args_dir(packager_env, args, 'tarball_source_dir_override')
    if tarball_source_dir_override_args:
      tarball_source_dir_override = tarball_source_dir_override_args['tarball_source_dir_override']
      tmp_tarball_filename = '%s.tar.gz' % (packager_env.package_descriptor.full_name)
      tmp_tarball_path = path.join(packager_env.tmp_dir, tmp_tarball_filename)
      archiver.create(tmp_tarball_path, tarball_source_dir_override, base_dir = packager_env.package_descriptor.full_name)
      tarballs_dict = { 'tarballs': [ tmp_tarball_path ] }
    else:
      tarballs_dict = clazz.resolve_step_args_files(packager_env, args, 'tarballs')
    if not tarballs_dict['tarballs']:
      tarball_name = args.get('tarball_name', packager_env.package_descriptor.name)
      tarball = clazz._find_tarball([ packager_env.source_dir, packager_env.download_dir ],
                                    tarball_name,
                                    packager_env.package_descriptor.version)
      if tarball:
        tarballs_dict = { 'tarballs': [ tarball ] }
      else:
        tarballs_dict = { 'tarballs': [] }
    extra_tarballs_dict = clazz.resolve_step_args_files(packager_env, args, 'extra_tarballs')

    assert tarballs_dict
    assert isinstance(tarballs_dict, dict)
    assert 'tarballs' in tarballs_dict
    assert 'extra_tarballs' not in tarballs_dict

    assert extra_tarballs_dict
    assert isinstance(extra_tarballs_dict, dict)
    assert 'extra_tarballs' in extra_tarballs_dict
    assert 'tarballs' not in extra_tarballs_dict

    return dict_util.combine(tarballs_dict, extra_tarballs_dict)

  @classmethod
  def _find_tarball(clazz, where, name, version):
    tarball = TarballUtil.find(where, name, version.upstream_version)

    if len(tarball) > 1:
      raise RuntimeError('Too many tarballs found for %s-%s: %s' % (name, version.upstream_version, ' '.join(tarball)))

    if len(tarball) == 0:
      return None #raise RuntimeError('No tarball found for for %s-%s in %s' % (name, version.upstream_version, where))

    tarball = tarball[0]

    if not archiver.is_valid(tarball):
      raise RuntimeError('Unknown archive type: %s' % (tarball))

    return tarball
