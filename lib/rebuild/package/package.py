#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, json, os.path as path, re

from bes.archive import archive, archiver
from bes.common import check, dict_util, json_util, string_util
from bes.fs import dir_util, file_check, file_find, file_mime, file_search, file_util, temp_file
from bes.match import matcher_filename
from bes.python import setup_tools
from rebuild.base import build_target, package_descriptor

from .package_metadata import package_metadata

class package(object):

  METADATA_DIR = 'metadata'
  INFO_FILENAME = METADATA_DIR + '/' + 'info.json'
  FILES_DIR = 'files'
  ENV_DIR = 'env'

  def __init__(self, tarball):
    file_check.check_file(tarball)
    assert archiver.is_valid(tarball)
    self.tarball = tarball
    self._descriptor = None
    self._files = None
    self._metadata = None
    self._raw_metadata = None

  @property
  def metadata(self):
    if not self._metadata:
      self._metadata = package_metadata.parse_json(self.raw_metadata)
    return self._metadata

  @property
  def raw_metadata(self):
    if not self._raw_metadata:
      # FIXME: need to use a better root dir something that ends up in ~/.rebuild/tmp/package_members_cache or such
      self._raw_metadata = archiver.extract_member_to_string_cached(self.tarball, self.INFO_FILENAME)
    return self._raw_metadata
  
  @property
  def descriptor(self):
    return self.metadata.descriptor

  @property
  def system(self):
    return self.metadata.system

  @property
  def build_target(self):
    return self.metadata.build_target

  @property
  def files(self):
    if not self._files:
      self._files = self._read_files()
    return self._files

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
      '${REBUILD_PACKAGE_NAME}': self.descriptor.name,
      '${REBUILD_PACKAGE_DESCRIPTION}': self.descriptor.name,
      '${REBUILD_PACKAGE_VERSION}': str(self.descriptor.version),
      '${REBUILD_PACKAGE_FULL_NAME}': self.descriptor.full_name,
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
  def descriptor_cmp(clazz, p1, p2):
    'Compare descriptor and return an int either -1, 0, or 1'
    assert isinstance(p1, package)
    assert isinstance(p2, package)
    return package_descriptor.full_name_cmp(p1.descriptor, p2.descriptor)

  @classmethod
  def package_descriptor(clazz, tarball):
    return package(tarball).descriptor

  @classmethod
  def package_files(clazz, tarball):
    return package(tarball).files

  @classmethod
  def create_tarball(clazz, tarball_path, pkg_desc, build_target, stage_dir, env_dir):
    # Hack the export_compilation_flags_requirements property to be a plain string list instead of the masked config it is
    properties = copy.deepcopy(pkg_desc.properties)
    if 'export_compilation_flags_requirements' in properties:
      properties['export_compilation_flags_requirements'] = [ str(x) for x in properties['export_compilation_flags_requirements'] ]
    files = file_find.find(stage_dir, relative = True, file_type = file_find.FILE | file_find.LINK)
    metadata = package_metadata('',
                                '',
                                pkg_desc.name,
                                pkg_desc.version.upstream_version,
                                pkg_desc.version.revision,
                                pkg_desc.version.epoch,
                                build_target.system,
                                build_target.level,
                                build_target.archs,
                                build_target.distro,
                                pkg_desc.requirements,
                                properties,
                                files)
    metadata_filename = temp_file.make_temp_file(suffix = '.json')
    file_util.save(metadata_filename, content = metadata.to_json())
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
