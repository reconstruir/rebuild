#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os, os.path as path
from bes.archive import archiver
from bes.fs import file_replace, file_util
from refactor import files as refactor_files
from rebuild import build_os_env
from rebuild.package_manager.unit_test_packages import unit_test_packages
from rebuild import package_descriptor, requirement, version, build_os_env
from bes.fs import temp_file
from bes.common import Shell

def main():
  root = os.getcwd()
 
  PACKAGES = [
    ( 'fructose-3.4.5-6', 'water', '1.0.0' ),
    ( 'mercury-1.2.8-0', 'water', '1.0.0' ),
    ( 'arsenic-1.2.9-0', 'water', '1.0.0' ),
    ( 'fiber-1.0.0-0', 'water', '1.0.0' ),
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

if __name__ == '__main__':
  raise SystemExit(main())
  
