#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_util, temp_file
from bes.common import string_util
from rebuild.base import build_target
from rebuild.builder import builder, builder_config, builder_env
from rebuild.package import package
from rebuild.checksum import checksum_manager
from bes.git import git, repo as git_repo

from rebuild.source_finder import local_source_finder, source_finder_chain

class unit_test_packaging(object):

  __test__ = False

  @classmethod
  def build_autoconf_package(clazz, asserter, name, version, revision, tarball_dir):
    tmp_dir = temp_file.make_temp_dir()
    builder_script_content = clazz.make_recipe_v1_content(name, version, revision)
    builder_script = file_util.save(path.join(tmp_dir, 'build.py'), content = builder_script_content)
    tarball_filename = '%s-%s.tar.gz' % (name, version)
    tarball_path = path.join(tarball_dir, tarball_filename)
    file_util.copy(path.join(tarball_dir, tarball_filename), tmp_dir)
    filenames = [ builder_script ]
    bt = build_target()
    config = builder_config()
    # FIXME change this to the tarball_dir see if it works remove need for tmp_dir
    config.build_root = path.join(tmp_dir, 'BUILD')
    config.source_dir = tmp_dir
    config.no_network = True
    config.no_checksums = True
    config.verbose = True
    env = builder_env(config, filenames)
    builder = builder(env, filenames)
    script = env.script_manager.scripts[ name ]
    env.checksum_manager.ignore(script.descriptor.full_name)
    rv = builder.build_script(script, env)
    #runner.build_script(script, env)
    if not rv.status == builder.SCRIPT_SUCCESS:
      print(rv.status)
    asserter.assertEqual( builder.SCRIPT_SUCCESS, rv.status )
    tarball = rv.packager_result.output['published_tarball']
    package = package(tarball)
    return package
    
  @classmethod
  def make_recipe_v1_content(clazz, name, version, revision, requirements = None, tests = None):
    requirements = requirements or []
    assert isinstance(requirements, list)
    requirements = [ string_util.quote(req) for req in requirements ]
    tests = tests or []
    assert isinstance(tests, list)
    tests = [ string_util.quote(test) for test in tests ]
    return '''
def rebuild_recipes(env):
  configure_env = [
    'all: CFLAGS=-I${REBUILD_REQUIREMENTS_INCLUDE_DIR} LDFLAGS=\"-L${REBUILD_REQUIREMENTS_LIB_DIR}\"',
  ]
  tests = [
    %s
  ]
  return env.args(
    properties = env.args(
      name = '%s',
      version = '%s-%s',
      category = 'lib',
    ),
    requirements = [
      %s
    ],
    steps = [
      'step_autoconf', {
        'configure_env': configure_env,
        'tests': tests,
      }
    ],
  )
''' % ('\n,'.join(tests), name, version, revision, '\n,'.join(requirements))
    
  @classmethod
  def make_recipe_v1(clazz, tmp_dir, filename, name, version, revision, requirements = None, tests = None):
    content = clazz.make_recipe_v1_content(name, version, revision,
                                              requirements = requirements,
                                              tests = tests)
    filepath = path.join(tmp_dir, filename)
    file_util.save(filepath, content = content)
    return filepath

  @classmethod
  def make_recipe_v2_content(clazz, name, version, revision, requirements = None, tests = None):
    requirements = requirements or []
    assert isinstance(requirements, list)
    requirements = [ string_util.quote(req) for req in requirements ]
    tests = tests or []
    assert isinstance(tests, list)
    tests = [ string_util.quote(test) for test in tests ]
    return '''
!rebuildrecipe!

package %s-%s-%s
  properties
    category=lib
  build_requirements
    %s
  steps
    step_autoconf
      configure_env
        all: CFLAGS=-I${REBUILD_REQUIREMENTS_INCLUDE_DIR} LDFLAGS=\"-L${REBUILD_REQUIREMENTS_LIB_DIR}\"
      tests
        %s
''' % (name, version, revision, '\n,'.join(requirements), '\n,'.join(tests))
  
if __name__ == '__main__':
  unittest.main()

  
