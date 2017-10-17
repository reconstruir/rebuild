#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .source_finder import source_finder
from bes.git import repo
from rebuild import build_blurb
import os.path as path

class repo_source_finder(source_finder):

  def __init__(self, root, address, no_network = False):
    self.repo = repo(root, address)
    self.no_network = no_network
#    self.updated = False
    
  def find_source(self, name, version, system):
    print('find_source(root=%s, address=%s, name=%s, version=%s, system=%s)' % (self.repo.root, self.repo.address, name, version, system))
    self._update()
    return self._find_tarball(self.repo.root, name, version, system)

#  def update_once(self):
#    if self.updated:
#      return
#    self.update()
#    self.updated = True

  def _update(self):
    print('_update(root=%s, address=%s)' % (self.repo.root, self.repo.address))
    if self.no_network:
      build_blurb.blurb('build', 'Repo sources disabled due to no_network: %s' % (path.relpath(self.repo.root)))
    else:
      build_blurb.blurb('build', 'Updating repo sources: %s' % (path.relpath(self.repo.root)))
      self.repo.clone_or_pull()
    
