#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common.check import check
from bes.git.git_repo import git_repo
from rebuild.base.build_blurb import build_blurb

from .storage_base import storage_base

class storage_git_repo(storage_base):

  def __init__(self, root, address, no_network = False, update_only_once = False):
    self.repo = git_repo(root, address)
    self.no_network = no_network
    self.update_only_once = update_only_once
    self._updated = False

  def __str__(self):
    return 'git_repo:%s' % (self.repo)

  #@abstractmethod
  def reload_available(self):
    assert False, 'FIXME: need to write code that does git pull.'
  
  #@abstractmethod
  def find_tarball(self, filename):
    self._update_if_needed()
    return path.join(self.repo.root, filename)

  #@abstractmethod
  def ensure_source(self, filename):
    assert False
    
  #@abstractmethod
  def search(self, name):
    assert False
  
  def _update_once(self):
    if self._updated:
      return
    self._update()
    self._updated = True

  def _update(self):
    if self.no_network:
      build_blurb.blurb('rebuild', 'Repo source finder update disabled due to no_network: %s' % (path.relpath(self.repo.root)))
    else:
      build_blurb.blurb('rebuild', 'Updating repo sources: %s' % (path.relpath(self.repo.root)))
      self.repo.clone_or_pull()

  def _update_if_needed(self):
    if self.update_only_once:
      self._update_once()
    else:
      self._update()
  
  #@abstractmethod
  def upload(self, local_filename, remote_filename, local_checksum):
    assert False

  #@abstractmethod
  def set_properties(self, filename, properties):
    assert False
    
  #@abstractmethod
  def remote_checksum(self, remote_filename):
    assert False #return file_util.checksum('sha1', self.remote_filename_abs(remote_filename))

  #@abstractmethod
  def list_all_files(self):
    assert False
    
