from setuptools import setup, find_packages
from bes.setup import tools as bes_tools

setup(
  name = 'rebuild',
  version = '1.0.0',
  packages = find_packages(include = ['rebuild*']),
  zip_safe = True,
  author = 'Ramiro Estrugo',
  author_email = 'bes@fateware.com',
  include_package_data = True,
  package_data = {
    'rebuild': bes_tools.find_tests_if_wanted('rebuild'),
  },
  scripts = [
    '../bin/rebuild_ar.py',
    '../bin/rebuild_jail.py',
    '../bin/rebuild_ldd.py',
    '../bin/rebuild_macho.py',
    '../bin/rebuild_native_package.py',
    '../bin/rebuild_sudo_editor.py',
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
