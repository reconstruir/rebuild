#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step.compound_step import compound_step

class step_no_build(compound_step):
  from .step_artifact_create import step_artifact_create

  __steps__ = [
    step_artifact_create,
  ]
  def __init__(self):
    super(step_no_build, self).__init__()
    
