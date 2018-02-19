#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from setuptools import setup, find_packages

ver = {}
exec(open('rebuild/ver.py', 'r').read(), {}, ver)

setup(
  name = 'rebuild',
  version = ver['BES_VERSION'],
  packages = find_packages(include = ['rebuild*']),
  include_package_data = True,
  zip_safe = True,
  author = ver['BES_AUTHOR_NAME'],
  author_email = ver['BES_AUTHOR_EMAIL'],
  scripts = [
    '../bin/rebuild_ar.py',
    '../bin/rebuild_jail.py',
    '../bin/rebuild_ldd.py',
    '../bin/rebuild_macho.py',
    '../bin/rebuild_native_package.py',
    '../bin/rebuild_sudo_editor.py',
    '../bin/rebuild_update_tarball_address.py',
    '../bin/rebuilder.py',
    '../bin/remanager.py',
    'rebuild/tools/linux/armv7/pkg_config-0.29.1_rev1/bin/armv7l-unknown-linux-gnueabihf-pkg-config',
    'rebuild/tools/linux/armv7/pkg_config-0.29.1_rev1/bin/pkg-config',
    'rebuild/tools/linux/armv7/pkg_config-0.29.1_rev1/share/aclocal/pkg.m4',
    'rebuild/tools/linux/armv7/pkg_config-0.29.1_rev1/share/doc/pkg-config/pkg-config-guide.html',
    'rebuild/tools/linux/armv7/pkg_config-0.29.1_rev1/share/man/man1/pkg-config.1',
    'rebuild/tools/linux/x86_64/pkg_config-0.29.1_rev1/bin/pkg-config',
    'rebuild/tools/linux/x86_64/pkg_config-0.29.1_rev1/bin/x86_64-unknown-linux-gnu-pkg-config',
    'rebuild/tools/linux/x86_64/pkg_config-0.29.1_rev1/share/aclocal/pkg.m4',
    'rebuild/tools/linux/x86_64/pkg_config-0.29.1_rev1/share/doc/pkg-config/pkg-config-guide.html',
    'rebuild/tools/linux/x86_64/pkg_config-0.29.1_rev1/share/man/man1/pkg-config.1',
    'rebuild/tools/macos/x86_64/pkg_config-0.29.1_rev1/bin/pkg-config',
    'rebuild/tools/macos/x86_64/pkg_config-0.29.1_rev1/bin/x86_64-apple-darwin14.5.0-pkg-config',
    'rebuild/tools/macos/x86_64/pkg_config-0.29.1_rev1/share/aclocal/pkg.m4',
    'rebuild/tools/macos/x86_64/pkg_config-0.29.1_rev1/share/doc/pkg-config/pkg-config-guide.html',
    'rebuild/tools/macos/x86_64/pkg_config-0.29.1_rev1/share/man/man1/pkg-config.1',
  ],
)
