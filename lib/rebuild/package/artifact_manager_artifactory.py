#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.common import check
from bes.system import log
from bes.debug import debug_timer
from bes.fs import file_util

from rebuild.base import artifact_descriptor, build_blurb, requirement_manager
from rebuild.artifactory.artifactory_requests import artifactory_requests
from rebuild.artifactory.artifactory_address import artifactory_address

from .artifact_manager_base import artifact_manager_base
from .artifact_db import artifact_db

from .db_error import *

class artifact_manager_artifactory(artifact_manager_base):

  def __init__(self, local_cache_dir, config):
    check.check_storage_config(config)
    super(artifact_manager_artifactory, self).__init__()
    self._local_cache_dir = local_cache_dir
    file_util.mkdir(self._local_cache_dir)
    self._read_only = True
    self._db = artifact_db(path.join(self._local_cache_dir, 'artifacts.db'))
    self._config = config.get('download', 'artifactory')
    self._address = artifactory_address(self._config.values['hostname'],
                                        self._config.values['repo'],
                                        self._config.root_dir,
                                        'artifacts',
                                        None)
    self._load_remote_db()
    
  def _load_remote_db(self):
    packages = artifactory_requests.list_all_artifacts(self._address,
                                                        self._config.credentials.username,
                                                        self._config.credentials.password)
    for package in packages:
      self._db.add_or_replace_artifact(package)

  #@abstractmethod
  def artifact_path(self, package_descriptor, build_target, relative):
    assert False
    
  #@abstractmethod
  def publish(self, tarball, build_target, allow_replace, metadata):
    assert False
    
  #@abstractmethod
  def remove_artifact(self, artifact_descriptor):
    assert False
  
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
    return md.mutate_filename(path.join(self._local_cache_dir, md.filename))

  #@abstractmethod
  def download(self, adesc):
    check.check_artifact_descriptor(adesc)
    md = self.find_by_artifact_descriptor(adesc, True)
    if not md:
      raise NotInstalledError('package not found: %s' % (str(adesc)))
    filename_abs = path.join(self._local_cache_dir, md.filename)
    if path.isfile(md.filename):
      self.log_d('already downloaded: %s' % (filename_abs))
      return
    address = self._address.mutate_filename(md.filename)
    self.log_i('downloading: %s => %s' % (str(address), filename_abs))
    artifactory_requests.download_to_file(filename_abs,
                                          address,
                                          self._config.credentials.username,
                                          self._config.credentials.password)
  
  #@abstractmethod
  def needs_download(self, adesc):
    check.check_artifact_descriptor(adesc)
    md = self.find_by_artifact_descriptor(adesc, False)
    if not md:
      raise NotInstalledError('package not found: %s' % (str(adesc)))
    return not path.isfile(md.filename)
