#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check

class value_env(object):

  def __init__(self):
    self.download_manager = None

check.register_class(value_env, include_seq = False)
