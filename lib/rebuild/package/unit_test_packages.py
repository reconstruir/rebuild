#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path
from bes.common import dict_util, json_util, string_util
from bes.fs import file_util, temp_file, temp_item
from bes.archive import archiver
from rebuild.base import build_arch, build_system, build_target, package_descriptor, requirement, requirement_list
from rebuild.package import package, package_metadata as PM
from collections import namedtuple

class unit_test_packages(object):

  __test__ = False

  #ARCHS = [ 'x86_64' ]
  ARCHS = build_arch.DEFAULT_HOST_ARCHS
  
  TEST_PACKAGES = {
    'water-1.0.0-0': PM('', 'water', '1.0.0', 0, 0, 'macos', 'release', ARCHS, None, None, {}, []),
    'water-1.0.0-1': PM('', 'water', '1.0.0', 1, 0, 'macos', 'release', ARCHS, None, None, {}, []),
    'water-1.0.0-2': PM('', 'water', '1.0.0', 2, 0, 'macos', 'release', ARCHS, None, None, {}, []),
    'fiber-1.0.0-0': PM('', 'fiber', '1.0.0', 2, 0, 'macos', 'release', ARCHS, None, None, {}, []),
    'citrus-1.0.0-0': PM('', 'citrus', '1.0.0', 2, 0, 'macos', 'release', ARCHS, None, None, {}, []),
    'fructose-3.4.5-6': PM('', 'fructose', '3.4.5', 6, 0, 'macos', 'release', ARCHS, None, None, {}, []),
    'mercury-1.2.8-0': PM('', 'mercury', '1.2.8', 0, 0, 'macos', 'release', ARCHS, None, None, {}, []),
    'mercury-1.2.8-1': PM('', 'mercury', '1.2.8', 1, 0, 'macos', 'release', ARCHS, None, None, {}, []),
    'mercury-1.2.9-0': PM('', 'mercury', '1.2.9', 0, 0, 'macos', 'release', ARCHS, None, None, {}, []),
    'mercury_conflict-3.2.1-0': PM('', 'mercury_conflict', '3.2.1', 0, 0, 'macos', 'release', ARCHS, None, None, {}, []),
    'arsenic-1.2.9-0': PM('', 'arsenic', '1.2.9', 0, 0, 'macos', 'release', ARCHS, None, None, {}, []),
    'arsenic-1.2.9-1': PM('', 'arsenic', '1.2.9', 1, 0, 'macos', 'release', ARCHS, None, None, {}, []),
    'arsenic-1.2.10-0': PM('', 'arsenic', '1.2.10', 0, 0, 'macos', 'release', ARCHS, None, None, {}, []),
    'apple-1.2.3-1': PM('', 'apple', '1.2.3', 1, 0, 'macos', 'release', ARCHS, None, 'fruit >= 1.0.0', {}, []),
    'fruit-1.0.0-0': PM('', 'fruit', '1.0.0', 0, 0, 'macos', 'release', ARCHS, None, 'fructose >= 3.4.5-6 fiber >= 1.0.0-0 water >= 1.0.0-0', {}, []),
    'pear-1.2.3-1': PM('', 'pear', '1.2.3', 1, 0, 'macos', 'release', ARCHS, None, 'fruit >= 1.0.0', {}, []),
    'orange-6.5.4-3': PM('', 'orange', '6.5.4', 3, 0, 'macos', 'release', ARCHS, None, 'fruit >= 1.0.0-0 citrus >= 1.0.0-0', {}, []),
    'orange_juice-1.4.5-0': PM('', 'orange_juice', '1.4.5', 0, 0, 'macos', 'release', ARCHS, None, 'orange >= 6.5.4-3', {}, []),
    'pear_juice-6.6.6-0': PM('', 'pear_juice', '6.6.6', 0, 0, 'macos', 'release', ARCHS, None, 'pear >= 1.2.3-1', {}, []),
    'smoothie-1.0.0-0': PM('', 'smoothie', '1.0.0', 0, 0, 'macos', 'release', ARCHS, None, 'orange >= 6.5.4-3 pear >= 1.2.3-1 apple >= 1.2.3-1', {}, []),
   }
  
  def __init__(self, desc, pm, system = 'macos', level = 'release', debug = False):
    self.desc = desc
    self.pm = PM(pm.filename,
                 pm.name,
                 pm.version,
                 pm.revision,
                 pm.epoch,
                 system,
                 level,
                 pm.archs,
                 pm.distro,
                 pm.requirements,
                 pm.properties,
                 pm.files,
                 pm.checksum)
    self.system = system
    self.level = level
    self.debug = debug

  def create_tarball(self, root_dir):
    package = self.make_test_package(self.pm, debug = self.debug)
    artifact_path = package.metadata.descriptor.artifact_path(package.metadata.build_target)
    target_path = path.join(root_dir, artifact_path)
    file_util.rename(package.tarball, target_path)
    if self.debug:
      print(('DEBUG: test_package.create_tarball() package=%s' % (target_path)))
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
    tmp_tarball = temp_file.make_temp_file(prefix = pm.descriptor.full_name, suffix = '.tar.gz', delete = not debug)
    package.create_tarball(tmp_tarball, pm.descriptor, pm.build_target, tmp_stage_dir)
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
    tp = clazz(desc, pm, system = 'macos', level = 'release', debug = debug)
    return tp.create_tarball(tmp_dir)

  @classmethod
  def make_test_packages(clazz, packages, root_dir, debug = False):
    for system in [ 'macos', 'linux' ]:
      for level in [ 'release', 'debug' ]:
        for desc, pm in packages.items():
          tp = clazz(desc, pm, system = system, level = level, debug = debug)
          tp.create_tarball(root_dir)

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
