#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .source_finder import source_finder
from rebuild import TarballUtil, version as reb_version, build_target as reb_build_target
from bes.common import check_type

class local_source_finder(source_finder):

  def __init__(self, where):
    self.where = where
    
  def find_source(self, name, version, build_target):
    check_type.check_string(name, 'name')
    check_type.check(version, reb_version, 'reb_version')
    check_type.check(build_target, reb_build_target, 'reb_build_target')

    tarball = TarballUtil.find(self.where, name, version.upstream_version)

    # If we find more than one tarball it could be because there are 1 for each platform so
    # filter out only the ones that match the current build system target
    if len(tarball) > 1:
      pattern = '/%s/' % (build_target.system)
      tarball = [ t for t in tarball if pattern in t ]
      
    if len(tarball) > 1:
      raise RuntimeError('Too many tarballs found for %s-%s: %s' % (name, version.upstream_version, ' '.join(tarball)))
    if len(tarball) == 0:
      return None

    tarball = tarball[0]

    if not archiver.is_valid(tarball):
      raise RuntimeError('Unknown archive type: %s' % (tarball))

    return tarball
