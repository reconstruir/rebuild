#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.system.check import check
from bes.system.log import log
from bes.debug.debug_timer import debug_timer
from bes.fs.file_util import file_util

from bes.build.artifact_descriptor import artifact_descriptor
from bes.build.build_blurb import build_blurb
from bes.build.requirement_manager import requirement_manager
from rebuild.artifactory.artifactory_requests import artifactory_requests
from rebuild.storage.storage_address import storage_address

from .artifact_manager_base import artifact_manager_base
from .artifact_db import artifact_db

from .db_error import *

class artifact_manager_artifactory(artifact_manager_base):

  def __init__(self, config):
    super(artifact_manager_artifactory, self).__init__()
    check.check_artifact_manager_factory_config(config)
    self._config = config
    self._local_cache_dir = config.local_cache_dir
    file_util.mkdir(self._local_cache_dir)
    self._read_only = True
    self._db = artifact_db(path.join(self._local_cache_dir, 'artifacts.db'))
    self._address = storage_address(self._config.storage_config.location,
                                    self._config.storage_config.repo,
                                    self._config.storage_config.root_dir,
                                    'artifacts',
                                    None)
    self._load_remote_db()

  def __str__(self):
    return 'artifactory:%s' % (str(self._address))
    
  def _load_remote_db(self):
    self.log_d('_load_remote_db: start. address={}'.format(str(self._address)))
    packages = artifactory_requests.list_artifacts(self._address,
                                                   self._config.storage_config.download)
    self.log_d('_load_remote_db: packages={}'.format(str(packages)))
    for package in sorted(packages, key = lambda x: tuple(x)):
      if not self._db.has_artifact(package.artifact_descriptor):
        self.log_i('importing remote package: %s' % (str(package.artifact_descriptor)))
        self._db.add_or_replace_artifact(package)
    self.log_i('_load_remote_db() end')

  #@abstractmethod
  def artifact_path(self, pkg_desc, build_target, relative):
    check.check_package_descriptor(pkg_desc)
    check.check_build_target(build_target)
    check.check_bool(relative)
    md = self.find_by_package_descriptor(pkg_desc, build_target, relative)
    return md.filename
    
  #@abstractmethod
  def publish(self, tarball, allow_replace, metadata):
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
      self.log_e('already downloaded: %s' % (filename_abs))
      return
    address = self._address.mutate_filename(md.filename)
    self.log_i('downloading: %s => %s' % (str(address), filename_abs))
    artifactory_requests.download_to_file(filename_abs,
                                          address,
                                          self._config.storage_config.download)
  
  #@abstractmethod
  def needs_download(self, adesc):
    check.check_artifact_descriptor(adesc)
    md = self.find_by_artifact_descriptor(adesc, False)
    if not md:
      raise NotInstalledError('package not found: %s' % (str(adesc)))
    return not path.isfile(md.filename)
