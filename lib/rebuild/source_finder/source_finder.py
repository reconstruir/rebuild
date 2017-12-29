#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.archive import archiver
from bes.common import check
from rebuild.base import build_system
from .tarball_finder import tarball_finder

class source_finder(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def find_source(self, name, version, build_target):
    pass

  @classmethod
  def _find_tarball(clazz, where, name, version, system):
    check.check_string(name, 'name')
    check.check_string(version, 'version')
    check.check_string(system, 'system')
    tarballs = tarball_finder.find(where, name, version)
    tarball = clazz._determine_tarball(tarballs, name, version, system)
    if not tarball:
      return None
    clazz._check_archive_valid(tarball)
    return tarball

  @classmethod
  def _determine_tarball(clazz, tarballs, name, version, system):
    if not tarballs:
      return None
    if len(tarballs) == 1:
      return tarballs[0]
    too_many_tarballs = []
    for tarball in tarballs:
      if clazz._tarball_is_platform_specific(tarball):
        if clazz._tarball_matches_system(tarball, system):
          return tarball
      else:
        too_many_tarballs.append(tarball)

    if len(too_many_tarballs) > 1:
      raise RuntimeError('Too many tarballs found for %s-%s: %s' % (name, version, ' '.join(too_many_tarballs)))

    return None
  
  @classmethod
  def _check_archive_valid(clazz, filename):
    if not archiver.is_valid(filename):
      raise RuntimeError('Invalid archive type: %s' % (filename))

  @classmethod
  def _tarball_is_platform_specific(clazz, tarball):
    for system in build_system.SYSTEMS:
      if clazz._tarball_matches_system(tarball, system):
        return True
    return False
    
  @classmethod
  def _tarball_matches_system(clazz, tarball, system):
    pattern = '/%s/' % (system)
    return pattern in tarball
