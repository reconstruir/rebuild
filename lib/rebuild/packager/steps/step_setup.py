#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import compound_step

from .step_setup_copy_source_to_build_dir import step_setup_copy_source_to_build_dir
from .step_setup_install_build_requirements import step_setup_install_build_requirements
from .step_setup_install_requirements import step_setup_install_requirements
from .step_setup_patch import step_setup_patch
from .step_setup_post_setup_hook import step_setup_post_setup_hook
from .step_setup_post_unpack_hook import step_setup_post_unpack_hook
from .step_setup_prepare_environment import step_setup_prepare_environment
from .step_setup_tarball_download import step_setup_tarball_download
from .step_setup_unpack import step_setup_unpack

class step_setup(compound_step):
  'A collection of multiple setup steps.'
  __steps__ = [
    step_setup_prepare_environment,
    step_setup_install_build_requirements,
    step_setup_tarball_download,
    step_setup_unpack,
    step_setup_patch,
    step_setup_post_unpack_hook,
    step_setup_copy_source_to_build_dir,
    step_setup_install_requirements,
    step_setup_post_setup_hook,
  ]
  def __init__(self):
    super(step_setup, self).__init__()
