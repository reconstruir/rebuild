#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from setuptools import setup, find_packages

ver = {}
exec(open('lib/rebuild/ver.py', 'r').read(), {}, ver)

setup(
  name = 'rebuild',
  version = ver['BES_VERSION'],
  packages = find_packages('lib'),
  package_dir= {'' : 'lib'},
  include_package_data = True,
  zip_safe = True,
  author = ver['BES_AUTHOR_NAME'],
  author_email = ver['BES_AUTHOR_EMAIL'],
  scripts = [
    'bin/rebuild_ar_replacement.py',
    'bin/rebuild_jail.py',
    'bin/rebuild_ldd.py',
    'bin/rebuild_macho.py',
    'bin/rebuild_native_package.py',
    'bin/rebuild_sudo_editor.py',
    'bin/rebuild_update_tarball_address.py',
    'bin/rebuilder.py',
    'bin/revenv.py',
  ],
)
