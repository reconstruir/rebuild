#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
from bes.archive import archiver
from bes.fs import file_replace, file_util, tar_util
from bes.refactor import files as refactor_files
from rebuild.package.unit_test_packages import unit_test_packages
from rebuild.base import build_os_env, package_descriptor, requirement
from bes.fs import temp_file
from bes.common import Shell

def main():
  root = os.getcwd()
  template_name = 'template'
  template_version = '1.0.0'
  template_dir = '%s-%s' % (template_name, template_version)
  make_template_tarball(root, template_name, template_version)
  PACKAGES = [
    ( 'fructose-3.4.5-6', template_name, template_version ),
    ( 'mercury-1.2.8-0', template_name, template_version ),
    ( 'arsenic-1.2.9-0', template_name, template_version ),
    ( 'fiber-1.0.0-0', template_name, template_version ),
    ( 'pear-1.2.3-1', 'apple', '1.2.3' ),
    ( 'orange-6.5.4-3', 'apple', '1.2.3' ),
   ]

  for package, template_name, template_version in PACKAGES:
    template_tarball = path.join(root, '%s-%s.tar.gz' % (template_name, template_version))
    tmp_dir = temp_file.make_temp_dir()
    desc = unit_test_packages.TEST_PACKAGES[package]
    pi = desc['package_info']

    version_no_revision = '%s-%s' % (pi.name, pi.version.upstream_version)

    archiver.extract(template_tarball, tmp_dir, base_dir = 'foo', strip_common_base = True)
    working_dir = path.join(tmp_dir, 'foo')
    refactor_files.refactor(template_name, pi.name, [ working_dir ])
    configure_ac_path = path.join(working_dir, 'configure.ac')

    replacements = { '[%s]' % (template_version): '[%s]' % (pi.version.upstream_version) }
    file_replace.replace(configure_ac_path, replacements, backup = False)

    command = [
      'cd %s' % (working_dir),
      'automake -a',
      'autoconf',
      './configure',
      'make dist',
      'cp %s.tar.gz %s' % (version_no_revision, root),
    ]
    env = build_os_env.make_clean_env(keep_keys = [ 'PATH' ])
    env['GZIP'] = '-n'
    Shell.execute(' && '.join(command), shell = True, non_blocking = True, env = env)

def make_template_tarball(root, template_name, template_version):
  tmp_dir = temp_file.make_temp_dir(delete = False)
  full_name = '%s-%s' % (template_name, template_version)
  template_dir = path.join(root, 'template')
  tar_util.copy_tree_with_tar(template_dir, tmp_dir)
  working_dir = path.join(tmp_dir, full_name)
  tarball_filename = '%s.tar.gz' % (full_name)
  command = [
    'cd %s' % (working_dir),
    'automake -a',
    'autoconf',
    './configure',
    'make dist',
    'cp %s %s' % (tarball_filename, root),
    ]
  env = build_os_env.make_clean_env(keep_keys = [ 'PATH' ])
  env['GZIP'] = '-n'
  Shell.execute(' && '.join(command), shell = True, non_blocking = True, env = env)
    
if __name__ == '__main__':
  raise SystemExit(main())
  