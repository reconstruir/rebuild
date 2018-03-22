#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path, re

from bes.archive import archive, archiver
from bes.common import check, dict_util, json_util, string_util
from bes.fs import dir_util, file_replace, file_search, file_mime, file_util, temp_file
from bes.match import matcher_filename
from bes.python import setup_tools
from rebuild.base import build_target, package_descriptor

class package(object):

  METADATA_DIR = 'metadata'
  INFO_FILENAME = METADATA_DIR + '/' + 'info.json'
  FILES_DIR = 'files'
  ENV_DIR = 'env'

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
  def build_target(self):
    return build_target(system = self.metadata['system'],
                        level = self.metadata['level'],
                        archs = self.metadata['archs'],
                        distro = self.metadata['distro'])

  @property
  def files(self):
    if not self._files:
      self._files = self._read_files()
    return self._files

  def _load_descriptor(self):
    return package_descriptor.parse_dict(self.metadata)

  def _load_metadata(self):
    # FIXME: need to use a better root dir something that ends up in ~/.rebuild/tmp/package_members_cache or such
    content = archiver.extract_member_to_string_cached(self.tarball, self.INFO_FILENAME)
    return json.loads(content)

  def _read_files(self):
    'Return the list of files in the package.  Only files no metadata.'
    files = [ m for m in archiver.members(self.tarball) if m.startswith(self.FILES_DIR) ]
    files = [ file_util.remove_head(f, self.FILES_DIR) for f in files ]
    return files

  def extract_files(self, installation_dir):
    archiver.extract(self.tarball, installation_dir,
                     strip_head = self.FILES_DIR,
                     include = self.FILES_DIR + '/*')
    self._post_install_hooks(installation_dir)

  def extract_env_files(self, env_dir, installation_dir):
    archiver.extract(self.tarball, env_dir,
                     strip_head = self.ENV_DIR,
                     include = self.ENV_DIR + '/*')
    self._variable_substitution_hook(env_dir, installation_dir)
    
  def _update_python_config_files(self, installation_dir):
    python_lib_dir = path.join(installation_dir, 'lib/python')
    setup_tools.update_egg_directory(python_lib_dir)

  def _variable_substitution_hook(self, where, installation_dir):
    replacements = {
      '${REBUILD_PACKAGE_PREFIX}': installation_dir,
      '${REBUILD_PACKAGE_NAME}': self.info.name,
      '${REBUILD_PACKAGE_DESCRIPTION}': self.info.name,
      '${REBUILD_PACKAGE_VERSION}': str(self.info.version),
      '${REBUILD_PACKAGE_FULL_NAME}': self.info.full_name,
    }
    file_search.search_replace(where,
                               replacements,
                               backup = False,
                               test_func = file_mime.is_text)

  def _post_install_hooks(self, installation_dir):
    self._update_python_config_files(installation_dir)
    self._variable_substitution_hook(installation_dir, installation_dir)
    
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
    assert isinstance(p1, package)
    assert isinstance(p2, package)
    return package_descriptor.full_name_cmp(p1.info, p2.info)

  @classmethod
  def package_info(clazz, tarball):
    return package(tarball).info

  @classmethod
  def package_files(clazz, tarball):
    return package(tarball).files

  @classmethod
  def create_tarball(clazz, tarball_path, pkg_desc, build_target, stage_dir, env_dir):
    metadata_dict = dict_util.combine(pkg_desc.to_dict(), build_target.to_dict())
    assert 'properties' in metadata_dict
    metadata = json_util.to_json(metadata_dict, indent = 2)
    metadata_filename = temp_file.make_temp_file(suffix = '.json')
    file_util.save(metadata_filename, content = metadata)
    extra_items = [
      archive.Item(metadata_filename, 'metadata/info.json'),
    ]
    if env_dir and path.isdir(env_dir):
      env_files = dir_util.list(env_dir, relative = True)
      for env_file in env_files:
        extra_items.append(archive.Item(path.join(env_dir, env_file), 'env' + '/' + env_file))
    archiver.create(tarball_path, stage_dir,
                    base_dir = 'files',
                    extra_items = extra_items,
                    exclude = '*.pc.bak')
    return tarball_path
  
check.register_class(package)
