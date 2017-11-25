#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from rebuild.step_manager import compound_step, step, step_call_hooks, step_result

class step_no_build(compound_step):
  'A simple uber step for autoconf projects.'
  from .step_artifact_create import step_artifact_create

  __steps__ = [
    step_artifact_create,
  ]
  def __init__(self):
    super(step_no_build, self).__init__()
    
