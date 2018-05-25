#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check

class recipe_load_env(object):

  def __init__(self, build_target = None, downloads_manager = None, source_finder = None):
    if build_target:
      check.check_build_target(build_target)
    self._build_target = build_target
    if downloads_manager:
      check.check_git_download_cache(downloads_manager)
    self._downloads_manager = downloads_manager
    if source_finder:
      check.check_source_finder_chain(source_finder)
    self._source_finder = source_finder

  @property
  def build_target(self):
    return self._build_target

  @property
  def downloads_manager(self):
    return self._downloads_manager

  @property
  def source_finder(self):
    return self._source_finder
  
check.register_class(recipe_load_env, include_seq = False)
