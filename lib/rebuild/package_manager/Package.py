#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path, re

from bes.archive import archiver
from rebuild import package_descriptor
from bes.fs import file_replace, file_search, file_mime, file_util
from bes.common import string_util
from bes.match import matcher_filename
from rebuild.pkg_config import pkg_config_file
from bes.python import setup_tools

class Package(object):

  METADATA_DIR = 'metadata'
  INFO_FILENAME = METADATA_DIR + '/' + 'info.json'
  FILES_DIR = 'files'

  def __init__(self, tarball):
    assert string_util.is_string(tarball)
    assert archiver.is_valid(tarball)
    self.tarball = tarball
    self._info = None
    self._files = None
    self._metadata = None

  @property
  def metadata(self):
    if not self._metadata:
      self._metadata = self._load_metadata()
    return self._metadata
    
  @property
  def info(self):
    if not self._info:
      self._info = self._load_descriptor()
    return self._info

  @property
  def system(self):
    return self.metadata['system']

  @property
  def files(self):
    if not self._files:
      self._files = self.__read_files()
    return self._files

  def _load_descriptor(self):
    return package_descriptor.parse_dict(self.metadata)

  def _load_metadata(self):
    # FIXME: need to use a better root dir something that ends up in ~/.rebbe/pacakge_members_cache or such
    content = archiver.extract_member_to_string_cached(self.tarball, self.INFO_FILENAME)
    return json.loads(content)

  def __read_files(self):
    'Return the list of files in the package.  Only files no metadata.'
    files = [ m for m in archiver.members(self.tarball) if m.startswith(self.FILES_DIR) ]
    files = [ file_util.remove_head(f, self.FILES_DIR) for f in files ]
    return files

  def extract_files(self, installation_dir):
    archiver.extract(self.tarball, installation_dir,
                     strip_head = self.FILES_DIR,
                     exclude = self.METADATA_DIR + '/*')
    self.__post_install_hooks(installation_dir)

  def __update_python_config_files(self, installation_dir):
    python_lib_dir = path.join(installation_dir, 'lib/python')
    setup_tools.update_egg_directory(python_lib_dir)

  def __rebbe_variable_substitution_hook(self, installation_dir):
    replacements = {
      '${REBUILD_PACKAGE_PREFIX}': installation_dir,
      '${REBUILD_PACKAGE_NAME}': self.info.name,
      '${REBUILD_PACKAGE_DESCRIPTION}': self.info.name,
      '${REBUILD_PACKAGE_VERSION}': str(self.info.version),
    }
    file_search.search_replace(installation_dir,
                               replacements,
                               backup = False,
                               test_func = file_mime.is_text)

  def __post_install_hooks(self, installation_dir):
    self.__update_python_config_files(installation_dir)
    self.__rebbe_variable_substitution_hook(installation_dir)
    
  def __is_old_crappy_config_file(self, filename):
    assert path.isfile(filename)
    if path.islink(filename):
      return False
    with open(filename, 'r') as fp:
      first_two = fp.read(2)
      if first_two == '#!':
        return True
    return False

  @property
  def pkg_config_files(self):
    return matcher_filename('*.pc').filter(self.files)

  @property
  def old_crappy_config_files(self):
    return matcher_filename('*-config').filter(self.files)

  @classmethod
  def package_is_valid(clazz, tarball):
    'Return True if the given archive is a valid package.'
    # FIXME: Maybe check some more stuff
    return archiver.is_valid(tarball)

  @classmethod
  def info_cmp(clazz, p1, p2):
    'Compare info and return an int either -1, 0, or 1'
    assert isinstance(p1, Package)
    assert isinstance(p2, Package)
    return package_descriptor.full_name_cmp(p1.info, p2.info)

  @classmethod
  def package_info(clazz, tarball):
    return Package(tarball).info

  @classmethod
  def package_files(clazz, tarball):
    return Package(tarball).files

