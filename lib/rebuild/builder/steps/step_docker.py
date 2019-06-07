#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common.check import check
from bes.fs.file_util import file_util
from rebuild.step import compound_step, step, step_result
from rebuild.toolchain import toolchain
from rebuild.docker.build_result import build_result

class step_docker_build(step):

  def __init__(self):
    super(step_docker_build, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    docker_flags   string_list
    docker_env     key_values
    dockerfile     string      Dockerfile
    dockertag      string
    '''
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    docker_env = values.get('docker_env')
    docker_flags = values.get('docker_flags') or []
    dockerfile = values.get('dockerfile')
    dockertag = values.get('dockertag')

    if check.is_string_list(docker_flags):
      docker_flags = docker_flags.to_list()
    else:
      assert isinstance(docker_flags, list)

#    tc = toolchain.get_toolchain(script.build_target)
      
#    dockerfile_path = path.join(script.source_unpacked_dir, dockerfile)
#    if not path.isfile(dockerfile_path):
    dockerfile_path = path.join(script.recipe_dir, dockerfile)

    if not path.isfile(dockerfile_path):
      return step_result(False, 'dockerfile script not found: %s' % (path.relpath(dockerfile_path)))
    
    docker_cmd = [
      'docker', 'build', 
      '--file', dockerfile_path,
      '--tag', dockertag,
      script.recipe_dir,
#      '--prefix=%s' % (script.staged_files_dir),
    ] # + docker_flags + tc.autoconf_flags()

    result = self.call_shell(docker_cmd, script, env,
                             shell_env = docker_env)
    if result.success:
      info = build_result.parse_build_result(result.stdout)
      print('CACA: %s' % (str(info)))
      if info.image_id:
        filename = '%s.image' % (script.descriptor.name)
        p = path.join(script.staged_files_dir, 'share', 'docker_rebuild', filename)
        file_util.save(p, content = info.image_id)
    return result
    # save_logs = [ 'config.log', 'config.status' ])

class step_docker(compound_step):
  'A compound step for docker projects.'
  from .step_setup import step_setup
  from .step_post_install import step_post_install
  
  __steps__ = [
    step_setup,
    step_docker_build,
    step_post_install,
  ]
  def __init__(self):
    super(step_docker, self).__init__()
