#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import compound_step

class step_post_install(compound_step):
  'Everything that needs to happen after the install step.'

  from .step_artifact_create import step_artifact_create
  from .step_check_darwin_archs import step_check_darwin_archs
  from .step_check_hard_coded_paths import step_check_hard_coded_paths
  from .step_cleanup import step_cleanup
  from .step_install_delete_files import step_install_delete_files
  from .step_install_install_files import step_install_install_files
  from .step_install_post_install_hooks import step_install_post_install_hooks
  from .step_make_instructions import step_make_instructions
  from .step_pkg_config_make_pc import step_pkg_config_make_pc
  from .step_install_env_files import step_install_env_files

  __steps__ = [
    step_install_delete_files,
    step_install_install_files,
    step_install_post_install_hooks,
    step_pkg_config_make_pc,
    step_install_env_files,
    step_make_instructions,
    step_check_hard_coded_paths,
    step_check_darwin_archs,
    step_cleanup,
    step_artifact_create,
  ]
  def __init__(self):
    super(step_post_install, self).__init__()
