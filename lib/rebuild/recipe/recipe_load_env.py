#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check

class recipe_load_env(object):

  def __init__(self, build_target, downloads_manager):
    #check.check_build_target(build_target)
    self.build_target = build_target
    self.downloads_manager = downloads_manager

check.register_class(recipe_load_env, include_seq = False)
