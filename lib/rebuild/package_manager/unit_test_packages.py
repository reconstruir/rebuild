#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path
from bes.common import dict_util, json_util, string_util
from bes.fs import file_util, temp_file, temp_item
from bes.archive import archiver
from rebuild import build_arch, build_target, Category, package_descriptor, requirement, System, version
from collections import namedtuple

class unit_test_packages(object):

  __test__ = False
  
  TEST_PACKAGES = {
    'water-1.0.0-0': {
      'requirements': '',
      'properties': { 'category': 'lib' },
    },
    'water-1.0.0-1': {
      'requirements': '',
      'properties': { 'category': 'lib' },
    },
    'water-1.0.0-2': {
      'requirements': '',
      'properties': { 'category': 'lib' },
    },
    'fiber-1.0.0-0': {
      'requirements': '',
      'properties': { 'category': 'lib' },
    },
    'fructose-3.4.5-6': {
      'requirements': '',
      'properties': { 'category': 'lib' },
    },
    'mercury-1.2.8-0': {
      'requirements': '',
      'properties': { 'category': 'lib' },
    },
    'mercury-1.2.8-1': {
      'requirements': '',
      'properties': { 'category': 'lib' },
    },
    'mercury-1.2.9-0': {
      'requirements': '',
      'properties': { 'category': 'lib' },
    },
    'mercury_conflict-3.2.1-0': {
      'requirements': '',
      'name_override': 'mercury',
      'properties': { 'category': 'lib' },
    },
    'arsenic-1.2.9-0': {
      'requirements': '',
      'properties': { 'category': 'lib' },
    },
    'arsenic-1.2.9-1': {
      'requirements': '',
      'properties': { 'category': 'lib' },
    },
    'arsenic-1.2.10-0': {
      'requirements': '',
      'properties': { 'category': 'lib' },
    },
    'apple-1.2.3-1': {
      'requirements': 'fructose(all) >= 3.4.5-6 fiber(all) >= 1.0.0-0',
      'properties': { 'category': 'lib' },
    },
    'pear-1.2.3-1': {
      'requirements': 'fructose(all) >= 3.4.5-6 fiber(all) >= 1.0.0-0',
      'properties': { 'category': 'lib' },
    },
    'orange-6.5.4-3': {
      'requirements': 'fructose(all) >= 3.4.5-6 fiber(all) >= 1.0.0-0',
      'properties': { 'category': 'lib' },
    },
    'orange_juice-1.4.5': {
      'requirements': 'orange(all) >= 6.5.4-3',
      'properties': { 'category': 'lib' },
    },
    'pear_juice-6.6.6': {
      'requirements': 'pear(all) >= 1.2.3-1',
      'properties': { 'category': 'lib' },
    },
   }
  for k, v in TEST_PACKAGES.items():
    template = TEST_PACKAGES[k]
    reqs = requirement.parse(template.get('requirements', ''))
    props = template.get('properties', {})
    pi = package_descriptor.parse(k)
    pi = package_descriptor(pi.name, pi.version, requirements = reqs, properties = props)
    template['package_info'] = pi
  
  def __init__(self, desc, requirements = None,
               system = 'macos', build_type = 'linux',
               properties = {}, name_override = None,
               debug = False):
    self.desc = desc
    self.requirements = requirements
    self.system = system
    self.build_type = build_type
    self.properties = properties
    self.name_override = name_override
    self.debug = debug

  def create_tarball(self, root_dir):
    pi = package_descriptor.parse(self.desc)
    reqs = requirement.parse(self.requirements)
    package = self.make_test_package(pi.name, pi.version, reqs,
                                     self.system, self.build_type,
                                     name_override = self.name_override,
                                     debug = self.debug)
    artifact_path = package.package_info.artifact_path(package.build_target)
    target_path = path.join(root_dir, artifact_path)
    file_util.rename(package.tarball, target_path)
    if self.debug:
      print(('DEBUG: test_package.create_tarball() package=%s' % (target_path)))
    return target_path

  test_package = namedtuple('test_package', 'tarball,package_info,build_target')

  @classmethod
  def make_test_package(clazz, name, version, requirements,
                        system, build_type, properties = None,
                        name_override = None, debug = False):
    props = { 'category': Category.LIB } 
    props.update(properties or {})
    pi = package_descriptor(name, version, requirements = requirements, properties = props)
    assert System.system_is_valid(system)
    bt = build_target(system, build_type, build_arch.ARCHS[system])
    metadata_dict = dict_util.combine(pi.to_dict(), bt.to_dict())
    metadata = json_util.to_json(metadata_dict, indent = 2)
    pkg_config_pc_contnet = clazz.make_pkg_config_pc_content(name, version)
    script_content = '#!/bin/bash\necho %s-%s\nexit 0\n' % (name, version)
    items = [
      temp_item('metadata/info.json', content = metadata),
      clazz.make_temp_item(name_override or name, version, '_foo.txt', 'docs'),
      clazz.make_temp_item(name_override or name, version, '_bar.txt', 'docs'),
      clazz.make_temp_item(name_override or name, version, '_script.sh', 'bin', content = script_content, mode = 0755),
      temp_item('files/lib/pkgconfig/%s.pc' % (name), content = pkg_config_pc_contnet)
    ]
    tmp_dir = temp_file.make_temp_dir(items = items, delete = not debug)
    tmp_tarball = temp_file.make_temp_file(prefix = pi.full_name, suffix = '.tar.gz', delete = not debug)
    archiver.create(tmp_tarball, tmp_dir)
    package = clazz.test_package(tmp_tarball, pi, bt)
    return package

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
    filename = 'files/%s/%s%s' % (location, name, suffix)
    if not content:
      content = 'package=%s-%s\nfilename=%s' % (name, version, filename)
    return temp_item(filename, content = content, mode = mode)
    
  @classmethod
  def make_simple_tarball(clazz, desc, templates, debug = False):
    tmp_dir = temp_file.make_temp_dir(delete = not debug)
    name_override = templates[desc].get('name_override', None)
    tp = clazz(desc, requirements = templates[desc]['requirements'],
               system = 'macos', build_type = 'release',
               name_override = name_override,
               debug = debug)
    return tp.create_tarball(tmp_dir)

  @classmethod
  def make_test_packages(clazz, packages, root_dir, debug = False):
    for system in [ 'macos', 'linux' ]:
      for bt in [ 'release', 'debug' ]:
        for desc, values in packages.items():
          tp = clazz(desc, values['requirements'], system, bt, properties = {}, debug = debug)
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
