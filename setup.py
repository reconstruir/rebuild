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
    'rebuild': bes_tools.find_tests('rebuild'),
  },
  scripts = [
    'bin/rebuild_ar.py',
    'bin/rebuild_jail.py',
    'bin/rebuild_ldd.py',
    'bin/rebuild_macho.py',
    'bin/rebuild_manager.py',
    'bin/rebuild_native_package.py',
    'bin/rebuild_sudo_editor.py',
    'bin/rebuilder.py',
  ],
)
