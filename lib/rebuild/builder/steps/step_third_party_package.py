#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import compound_step

class step_third_party_package(compound_step):
  'A complete step to make python eggs using the "bdist_egg" target of setuptools.'
  from .step_setup import step_setup
  from .step_post_install import step_post_install
  
  __steps__ = [
    step_setup,
    step_post_install,
  ]

  def __init__(self):
    super(step_third_party_package, self).__init__()
