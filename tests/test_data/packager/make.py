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

DEBUG = False
#DEBUG = True

def main():
  root = os.getcwd()
  make_template_tarball(root, 'template', '1.0.0')
  make_template_tarball(root, 'templatedepends', '1.2.3')
  PACKAGES = [
    ( 'fructose-3.4.5-6', 'template', '1.0.0' ),
    ( 'mercury-1.2.8-0', 'template', '1.0.0' ),
    ( 'arsenic-1.2.9-0', 'template', '1.0.0' ),
    ( 'fiber-1.0.0-0', 'template', '1.0.0' ),
    ( 'pear-1.2.3-1', 'templatedepends', '1.2.3' ),
    ( 'orange-6.5.4-3', 'templatedepends', '1.2.3' ),
   ]

  for package, template_name, template_version in PACKAGES:
    template_tarball = path.join(root, '%s-%s.tar.gz' % (template_name, template_version))
    tmp_dir = temp_file.make_temp_dir(delete = not DEBUG)
    desc = unit_test_packages.TEST_PACKAGES[package]
    pi = desc['package_info']

    version_no_revision = '%s-%s' % (pi.name, pi.version.upstream_version)

    archiver.extract(template_tarball, tmp_dir, base_dir = 'foo', strip_common_base = True)
    working_dir = path.join(tmp_dir, 'foo')
    if DEBUG:
      print('working_dir=%s' % (working_dir))
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
    flat_command = ' && '.join(command)
    Shell.execute(flat_command, shell = True, non_blocking = True, env = env)

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
  result = path.join(root, '%s-%s.tar.gz' % (template_name, template_version))
  assert path.isfile(result)
  return result
  
if __name__ == '__main__':
  raise SystemExit(main())
  
