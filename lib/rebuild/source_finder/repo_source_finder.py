#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .source_finder import source_finder
from bes.git import repo

class repo_source_finder(source_finder):

  def __init__(self, root, address, no_network):
    self.repo = repo(root, address)
    self.no_network = no_network
  
  def find_source(self, name, version, system):
    self.update_once()
    return self._find_tarball(self.repo.root, name, version, system)

  _UPDATED = False
  def update_once(self):
    if self._UPDATED:
      return
    self._UPDATED = True
    if self.no_network:
      self.blurb('Repo sources disabled due to no_network: %s' % (path.relpath(self.repo.root)))
    else:
      self.blurb('Updating repo sources: %s' % (path.relpath(self.repo.root)))
      self.repo.clone_or_pull()
