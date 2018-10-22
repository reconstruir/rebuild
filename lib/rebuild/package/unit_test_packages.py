#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import dict_util, json_util, string_util
from bes.fs import file_find, file_util, temp_file, temp_item
from bes.archive import archiver
from rebuild.base import build_arch, build_system, build_target, package_descriptor, requirement, requirement_list
from rebuild.package import package, package_files, package_metadata as PM
from collections import namedtuple

class unit_test_packages(object):

  __test__ = False

  FILES = package_files([], [])
  TEST_PACKAGES = {
    'water-1.0.0-0': PM('', 'water', '1.0.0', 0, 0, 'macos', 'release', 'x86_64', '', '', None, {}, FILES),
    'water-1.0.0-1': PM('', 'water', '1.0.0', 1, 0, 'macos', 'release', 'x86_64', '', '', None, {}, FILES),
    'water-1.0.0-2': PM('', 'water', '1.0.0', 2, 0, 'macos', 'release', 'x86_64', '', '', None, {}, FILES),
    'fiber-1.0.0-0': PM('', 'fiber', '1.0.0', 0, 0, 'macos', 'release', 'x86_64', '', '', None, {}, FILES),
    'citrus-1.0.0-0': PM('', 'citrus', '1.0.0', 2, 0, 'macos', 'release', 'x86_64', '', '', None, {}, FILES),
    'fructose-3.4.5-6': PM('', 'fructose', '3.4.5', 6, 0, 'macos', 'release', 'x86_64', '', '', None, {}, FILES),
    'mercury-1.2.8-0': PM('', 'mercury', '1.2.8', 0, 0, 'macos', 'release', 'x86_64', '', '', None, {}, FILES),
    'mercury-1.2.8-1': PM('', 'mercury', '1.2.8', 1, 0, 'macos', 'release', 'x86_64', '', '', None, {}, FILES),
    'mercury-1.2.9-0': PM('', 'mercury', '1.2.9', 0, 0, 'macos', 'release', 'x86_64', '', '', None, {}, FILES),
    'mercury_conflict-3.2.1-0': PM('', 'mercury_conflict', '3.2.1', 0, 0, 'macos', 'release', 'x86_64', '', '', None, {}, FILES),
    'arsenic-1.2.9-0': PM('', 'arsenic', '1.2.9', 0, 0, 'macos', 'release', 'x86_64', '', '', None, {}, FILES),
    'arsenic-1.2.9-1': PM('', 'arsenic', '1.2.9', 1, 0, 'macos', 'release', 'x86_64', '', '', None, {}, FILES),
    'arsenic-1.2.10-0': PM('', 'arsenic', '1.2.10', 0, 0, 'macos', 'release', 'x86_64', '', '', None, {}, FILES),
    'apple-1.2.3-1': PM('', 'apple', '1.2.3', 1, 0, 'macos', 'release', 'x86_64', '', '', 'fruit >= 1.0.0', {}, FILES),
    'fruit-1.0.0-0': PM('', 'fruit', '1.0.0', 0, 0, 'macos', 'release', 'x86_64', '', '', 'fructose >= 3.4.5-6 fiber >= 1.0.0-0 water >= 1.0.0-0', {}, FILES),
    'pear-1.2.3-1': PM('', 'pear', '1.2.3', 1, 0, 'macos', 'release', 'x86_64', '', '', 'fruit >= 1.0.0', {}, FILES),
    'orange-6.5.4-3': PM('', 'orange', '6.5.4', 3, 0, 'macos', 'release', 'x86_64', '', '', 'fruit >= 1.0.0-0 citrus >= 1.0.0-0', {}, FILES),
    'orange_juice-1.4.5-0': PM('', 'orange_juice', '1.4.5', 0, 0, 'macos', 'release', 'x86_64', '', '', 'orange >= 6.5.4-3', {}, FILES),
    'pear_juice-6.6.6-0': PM('', 'pear_juice', '6.6.6', 0, 0, 'macos', 'release', 'x86_64', '', '', 'pear >= 1.2.3-1', {}, FILES),
    'smoothie-1.0.0-0': PM('', 'smoothie', '1.0.0', 0, 0, 'macos', 'release', 'x86_64', '', '', 'orange >= 6.5.4-3 pear >= 1.2.3-1 apple >= 1.2.3-1', {}, FILES),
   }
  
  def __init__(self, desc, pm, system, level, distro, distro_version, debug = False):
    self.desc = desc
    self.pm = PM(pm.filename,
                 pm.name,
                 pm.version,
                 pm.revision,
                 pm.epoch,
                 system,
                 level,
                 pm.arch,
                 distro,
                 distro_version,
                 pm.requirements,
                 pm.properties,
                 pm.files)
    self.system = system
    self.level = level
    self.debug = debug

  def create_package(self, root_dir):
    package = self.make_test_package(self.pm, debug = self.debug)
    artifact_path = package.metadata.package_descriptor.artifact_path(package.metadata.build_target)
    target_path = path.join(root_dir, artifact_path)
    file_util.rename(package.tarball, target_path)
    if self.debug:
      print(('DEBUG: test_package.create_package() package=%s' % (target_path)))
    return target_path

  test_package = namedtuple('test_package', 'tarball,metadata')

  @classmethod
  def make_test_package(clazz, pm, debug = False):
    pkg_config_pc_contnet = clazz.make_pkg_config_pc_content(pm.name, pm.build_version)
    script_content = '#!/bin/bash\necho %s-%s\nexit 0\n' % (pm.name, pm.build_version)
    name = pm.name.replace('_conflict', '')
    items = [
      clazz.make_temp_item(name, pm.version, '_foo.txt', 'docs'),
      clazz.make_temp_item(name, pm.version, '_bar.txt', 'docs'),
      clazz.make_temp_item(name, pm.version, '_script.sh', 'bin', content = script_content, mode = 0o755),
      temp_item('lib/pkgconfig/%s.pc' % (name), content = pkg_config_pc_contnet)
    ]
    tmp_stage_dir = temp_file.make_temp_dir(delete = not debug)
    tmp_stage_files_dir = path.join(tmp_stage_dir, 'files')
    temp_file.write_temp_files(tmp_stage_files_dir, items)
    tmp_tarball = temp_file.make_temp_file(prefix = pm.package_descriptor.full_name, suffix = '.tar.gz', delete = not debug)
    package.create_package(tmp_tarball, pm.package_descriptor, pm.build_target, tmp_stage_dir)
    return clazz.test_package(tmp_tarball, pm)

  _PKG_CONFIG_PC_TEMPLATE = '''
prefix=${REBUILD_PACKAGE_PREFIX}
exec_prefix=${prefix}
libdir=${exec_prefix}/lib
includedir=${prefix}/include

Name: @NAME@
Description: @NAME@
Version: @VERSION@
Libs: -L${libdir} @LIBS@
Libs.private: @LIBS_PRIVATE@
Cflags: -I${includedir}
'''
  
  @classmethod
  def make_pkg_config_pc_content(clazz, name, version):
    replacemetns = {
      '@NAME@': name,
      '@VERSION@': version.upstream_version,
      '@LIBS@': '-l%s' % (name),
      '@LIBS_PRIVATE@': '-lpriv',
    }
    return string_util.replace(clazz._PKG_CONFIG_PC_TEMPLATE, replacemetns)

  @classmethod
  def make_temp_item(clazz, name, version, suffix, location, content = None, mode = None):
    filename = '%s/%s%s' % (location, name, suffix)
    if not content:
      content = 'package=%s-%s\nfilename=%s' % (name, version, filename)
    return temp_item(filename, content = content, mode = mode)
    
  @classmethod
  def make_simple_tarball(clazz, desc, templates, debug = False):
    tmp_dir = temp_file.make_temp_dir(delete = not debug)
    pm = templates[desc]
    tp = clazz(desc, pm, 'macos', 'release', '', '10.10', debug = debug)
    return tp.create_package(tmp_dir)

  @classmethod
  def make_test_packages(clazz, packages, root_dir, debug = False):
    for system in [ 'macos', 'linux' ]:
      for level in [ 'release', 'debug' ]:
        for desc, pm in packages.items():
          if system == 'linux':
            distro = 'ubuntu'
            distro_version = '18'
          else:
            distro = ''
            distro_version = '10.10'
          tp = clazz(desc, pm, system, level, distro, distro_version, debug = debug)
          tp.create_package(root_dir)

  @classmethod
  def publish_artifacts(clazz, am):
    artifacts = file_find.find_fnmatch(am.root_dir, [ '*.tar.gz' ], relative = False)
    for artifact in artifacts:
      tmp_artifact = temp_file.make_temp_file()
      file_util.copy(artifact, tmp_artifact)
      file_util.remove(artifact)
      p = package(tmp_artifact)
      am.publish(tmp_artifact, p.metadata.build_target, False)
          
  @classmethod
  def make_water(clazz, debug = False):
    return clazz.make_simple_tarball('water-1.0.0-0', clazz.TEST_PACKAGES, debug = debug)

  @classmethod
  def make_fiber(clazz, debug = False):
    return clazz.make_simple_tarball('fiber-1.0.0-0', clazz.TEST_PACKAGES, debug = debug)

  @classmethod
  def make_apple(clazz, debug = False):
    return clazz.make_simple_tarball('apple-1.2.3-1', clazz.TEST_PACKAGES, debug = debug)

  @classmethod
  def make_fruit(clazz, debug = False):
    return clazz.make_simple_tarball('fruit-1.0.0-0', clazz.TEST_PACKAGES, debug = debug)

  @classmethod
  def make_orange(clazz, debug = False):
    return clazz.make_simple_tarball('orange-6.5.4-3', clazz.TEST_PACKAGES, debug = debug)

  @classmethod
  def make_fructose(clazz, debug = False):
    return clazz.make_simple_tarball('fructose-3.4.5-6', clazz.TEST_PACKAGES, debug = debug)

  @classmethod
  def make_mercury(clazz, debug = False):
    return clazz.make_simple_tarball('mercury-1.2.8-0', clazz.TEST_PACKAGES, debug = debug)

  @classmethod
  def make_mercury_conflict(clazz, debug = False):
    return clazz.make_simple_tarball('mercury_conflict-3.2.1-0', clazz.TEST_PACKAGES, debug = debug)

  @classmethod
  def make_arsenic(clazz, debug = False):
    return clazz.make_simple_tarball('arsenic-1.2.9-0', clazz.TEST_PACKAGES, debug = debug)

  _TEST_PACKAGE_RECIPES='''
fake_package
  metadata
    name tool_foo
    version 1.2.3
    revision 0
    epoch 0
    system linux
    level release
    arch x86_64
    distro ubuntu
    distro_version 18
  
  files
    bin/tfoo.py
      #!/usr/bin/env python
      import sys
      def main():
        sys.stdout.write('tfoo: ')
        for i, arg in enumerate(sys.argv[1:]):
          if i != 0:
            sys.stdout.write(' ')
          sys.stdout.write(arg)
        sys.stdout.write('\n')
      
      if __name__ == '__main__':
        raise SystemExit(main())

  env_files
    tfoo_env.sh
      #@REBUILD_HEAD@
      export TFOO_ENV1=tfoo_env1
      export TFOO_ENV2=tfoo_env2
      #@REBUILD_TAIL@
'''  
