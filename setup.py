from setuptools import setup, find_packages

setup(
  name = 'rebuild',
  version = '1.0.0',
  packages = find_packages(),
  zip_safe = False,
  author = 'Ramiro Estrugo',
  author_email = 'bes@fateware.com',
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
