#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util
from bes.system import log
from rebuild.base import build_blurb
from bes.fs import file_util
from .artifact_manager_base import artifact_manager_base
from .artifact_db import artifact_db
from .db_error import *

#log.configure('artifact_manager=debug')

class artifact_manager_local(artifact_manager_base):

  def __init__(self, root_dir):
    super(artifact_manager_local, self).__init__()
    check.check_string(root_dir)
    self._root_dir = path.abspath(root_dir)
    file_util.mkdir(self._root_dir)
    self._db = artifact_db(path.join(self._root_dir, 'artifacts.db'))

  @property
  def root_dir(self):
    return self._root_dir

  #@abstractmethod
  def artifact_path(self, pkg_desc, build_target, relative):
    check.check_package_descriptor(pkg_desc)
    check.check_build_target(build_target)
    artifact_path_rel, artifact_path_abs = self._artifact_paths(pkg_desc, build_target)
    if not path.isfile(artifact_path_abs):
      return None
    if relative:
      return artifact_path_rel
    return artifact_path_abs

  def _artifact_paths(self, pkg_desc, build_target):
    filename = '%s.tar.gz' % (pkg_desc.full_name)
    artifact_path_rel = path.join(build_target.build_path, filename)
    artifact_path_abs = path.join(self._root_dir, artifact_path_rel)
    return artifact_path_rel, artifact_path_abs
  
  #@abstractmethod
  def publish(self, tarball, allow_replace, metadata):
    check.check_package_metadata(metadata)
    if self._read_only:
      raise RuntimeError('artifact_manager is read only.')
    check.check_package_metadata(metadata)
    pkg_desc = metadata.package_descriptor
    artifact_path_rel, artifact_path_abs = self._artifact_paths(pkg_desc, metadata.build_target)
    file_util.copy(tarball, artifact_path_abs, use_hard_link = True)
    self._reset_requirement_managers()
    pkg_metadata = metadata.mutate_filename(artifact_path_rel)
    should_replace = allow_replace and self._db.has_artifact(pkg_metadata.artifact_descriptor)
    if should_replace:
      self._db.replace_artifact(pkg_metadata)
    else:
      self._db.add_artifact(pkg_metadata)
    return artifact_path_abs

  #@abstractmethod
  def remove_artifact(self, adesc):
    check.check_artifact_descriptor(adesc)
    if self._read_only:
      raise RuntimeError('artifact_manager is read only.')
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
  def find_by_artifact_descriptor(self, adesc, relative_filename):
    check.check_artifact_descriptor(adesc)
    md = self._db.get_artifact(adesc)
    if relative_filename:
      return md
    return md.mutate_filename(path.join(self._root_dir, md.filename))

  #@abstractmethod
  def download(self, adesc):
    pass
  
  #@abstractmethod
  def needs_download(self, adesc):
    return False
