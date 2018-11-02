#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util
from bes.system import log
from rebuild.base import build_blurb
from bes.git import git
from bes.fs import file_util
from bes.debug import debug_timer, noop_debug_timer
from rebuild.base import requirement_manager

from .artifact_manager_base import artifact_manager_base
from .artifact_db import artifact_db
from .artifact_descriptor import artifact_descriptor
from .db_error import *
from .package import package

#log.configure('artifact_manager=debug')

class artifact_manager_local(artifact_manager_base):

  def __init__(self, root_dir):
    super(artifact_manager_local, self).__init__()
    check.check_string(root_dir)

    self._root_dir = path.abspath(root_dir)
    
    file_util.mkdir(self._root_dir)
    #self.log_d('Creating instance with root_dir=%s' % (self._root_dir))
    #self.blurb('Creating instance with root_dir=%s' % (self._root_dir))

    self._db = artifact_db(path.join(self._root_dir, 'artifacts.db'))
#    self._timer = debug_timer('am', 'error')
    self._timer = noop_debug_timer('am', 'error')
#    self._sync_db()

    self._db = artifact_db(path.join(self._root_dir, 'artifacts.db'))

  @property
  def root_dir(self):
    return self._root_dir
    
  #@abstractmethod
  def artifact_path(self, package_descriptor, build_target, relative):
    filename = '%s.tar.gz' % (package_descriptor.full_name)
    relative_path = path.join(build_target.build_path, filename)
    if relative:
      return relative_path
    return path.join(self._root_dir, relative_path)

  #@abstractmethod
  def publish(self, tarball, build_target, allow_replace, metadata):
    if not metadata:
      metadata = package(tarball).metadata
    check.check_package_metadata(metadata)
    pkg_desc = metadata.package_descriptor
    artifact_path_rel = self.artifact_path(pkg_desc, build_target, True)
    artifact_path_abs = self.artifact_path(pkg_desc, build_target, False)
    file_util.copy(tarball, artifact_path_abs, use_hard_link = True)
    self._reset_requirement_managers()
    pkg_metadata = metadata.clone_with_filename(artifact_path_rel)
    should_replace = allow_replace and self._db.has_artifact(pkg_metadata.artifact_descriptor)
    if should_replace:
      self._db.replace_artifact(pkg_metadata)
    else:
      self._db.add_artifact(pkg_metadata)
    return artifact_path_abs

  #@abstractmethod
  def remove_artifact(self, adesc):
    check.check_artifact_descriptor(adesc)
    md = self.find_by_artifact_descriptor(adesc, False)
    if not md:
      raise NotInstalledError('package \"%s\" not found' % (str(adesc)))
    file_util.remove(md.filename)
    self._db.remove_artifact(adesc)
  
  #@abstractmethod
  def list_all_by_descriptor(self, build_target):
    return self._db.list_all_by_descriptor(build_target)

  #@abstractmethod
  def list_all_by_metadata(self, build_target):
    return self._db.list_all_by_metadata(build_target)

  #@abstractmethod
  def list_all_by_package_descriptor(self, build_target):
    return self._db.list_all_by_package_descriptor(build_target)

  #@abstractmethod
  def find_by_package_descriptor(self, package_descriptor, build_target, relative_filename):
    check.check_package_descriptor(package_descriptor)
    check.check_build_target(build_target)
    adesc = artifact_descriptor(package_descriptor.name, package_descriptor.version.upstream_version,
                                package_descriptor.version.revision, package_descriptor.version.epoch,
                                build_target.system, build_target.level, build_target.arch,
                                build_target.distro, build_target.distro_version)
    return self.find_by_artifact_descriptor(adesc, relative_filename)

  #@abstractmethod
  def find_by_artifact_descriptor(self, adesc, relative_filename):
    check.check_artifact_descriptor(adesc)
    md = self._db.get_artifact(adesc)
    if relative_filename:
      return md
    return md.clone_with_filename(path.join(self._root_dir, md.filename))
  
  #@abstractmethod
  def _make_requirement_manager(self, build_target):
    self._timer.start('_make_requirement_manager() for %s' % (str(build_target)))
    rm = requirement_manager()
    latest_versions = self.list_all_by_package_descriptor(build_target).latest_versions()
    for pkg_desc in latest_versions:
      rm.add_package(pkg_desc)
    self._timer.stop()
    return rm
