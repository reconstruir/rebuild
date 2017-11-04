#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .source_finder import source_finder
from bes.git import repo
from rebuild.base import build_blurb
import os.path as path

class repo_source_finder(source_finder):

  def __init__(self, root, address, no_network = False, update_only_once = False):
    self.repo = repo(root, address)
    self.no_network = no_network
    self.update_only_once = update_only_once
    self._updated = False
    
  def find_source(self, name, version, system):
    if self.update_only_once:
      self._update_once()
    else:
      self._update()
    return self._find_tarball(self.repo.root, name, version, system)

  def _update_once(self):
    if self._updated:
      return
    self._update()
    self._updated = True

  def _update(self):
    if self.no_network:
      build_blurb.blurb('build', 'Repo source finder update disabled due to no_network: %s' % (path.relpath(self.repo.root)))
    else:
      build_blurb.blurb('build', 'Updating repo sources: %s' % (path.relpath(self.repo.root)))
      self.repo.clone_or_pull()
