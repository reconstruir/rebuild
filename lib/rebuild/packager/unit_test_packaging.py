#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path
from bes.fs import file_util, temp_file
from bes.common import string_util
from rebuild import build_target, version as rebuild_version
from rebuild.packager import build_script_runner, rebuild_builder, rebuild_config, rebuild_env
from rebuild.package_manager import Package
from rebuild.checksum import checksum_manager
from bes.git import git, repo as git_repo

from rebuild.source_finder import local_source_finder, source_finder_chain

class unit_test_packaging(object):

  __test__ = False

  @classmethod
  def build_script_runner_build_autoconf_package(clazz, asserter, name, version, revision, tarball_dir):
    tmp_dir = temp_file.make_temp_dir()
    build_script_content = clazz.make_build_script_content(name, version, revision)
    build_script = file_util.save(path.join(tmp_dir, 'build.py'), content = build_script_content)
    tarball_filename = '%s-%s.tar.gz' % (name, version)
    tarball_path = path.join(tarball_dir, tarball_filename)
    file_util.copy(path.join(tarball_dir, tarball_filename), tmp_dir)
    filenames = [ build_script ]
    bt = build_target()
    runner = build_script_runner(filenames, bt)
    script = runner.scripts[ name ]
    config = rebuild_config()
    # FIXME change this to the tarball_dir see if it works remove need for tmp_dir
    config.source_dir = tmp_dir
    config.no_network = True
    config.no_checksums = True
    config.verbose = True
    env = rebuild_env(tmp_dir, config)
    env.checksum_manager.ignore(script.package_info.full_name)
    rv = runner.run_build_script(script,
                                 env,
                                 tmp_dir = temp_file.make_temp_dir())
    if not rv.status == build_script_runner.SUCCESS:
      print(rv.status)
    asserter.assertEqual( build_script_runner.SUCCESS, rv.status )
    tarball = rv.packager_result.output['published_tarball']
    package = Package(tarball)
    return package
    
  @classmethod
  def make_build_script_content(clazz, name, version, revision, requirements = None, tests = None):
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
      step_autoconf, {
        'configure_env': configure_env,
        'tests': tests,
      }
    ],
  )
''' % ('\n,'.join(tests), name, version, revision, '\n,'.join(requirements))
    
  @classmethod
  def make_build_script(clazz, tmp_dir, filename, name, version, revision, requirements = None, tests = None):
    content = clazz.make_build_script_content(name, version, revision,
                                              requirements = requirements,
                                              tests = tests)
    filepath = path.join(tmp_dir, filename)
    file_util.save(filepath, content = content)
    return filepath
  
if __name__ == '__main__':
  unittest.main()

  
