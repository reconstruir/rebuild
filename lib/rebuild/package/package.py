#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, re

from bes.archive import archive, archiver
from bes.common import check, dict_util, json_util, string_util
from bes.fs import dir_util, file_check, file_checksum_list, file_find, file_mime, file_search, file_util, temp_file
from bes.text import text_line_parser
from bes.match import matcher_filename, matcher_multiple_filename
from bes.python import setup_tools
from bes.system import execute
from rebuild.base import build_target, package_descriptor
from bes.debug import noop_debug_timer

from .package_metadata import package_metadata
from .package_files import package_files

class package(object):

  METADATA_DIR = 'metadata'
  METADATA_FILENAME = METADATA_DIR + '/' + 'metadata.json'
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
      content = archiver.extract_member_to_string_cached(self.tarball, self.METADATA_FILENAME)
      self._raw_metadata = content.decode('utf-8')
    return self._raw_metadata
  
  @property
  def package_descriptor(self):
    return self.metadata.package_descriptor

  @property
  def artifact_descriptor(self):
    return self.metadata.artifact_descriptor

  @property
  def system(self):
    return self.metadata.system

  @property
  def build_target(self):
    return self.metadata.build_target

  @property
  def files(self):
    return self.metadata.files.files.filenames()

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

  _ENV_FILE_HEAD_TEMPLATE = '''\
_this_file="$( command readlink "$BASH_SOURCE" )" || _this_file="$BASH_SOURCE"
_unresolved_root="${_this_file%/*}"
REBUILD_ENV_DIR="$( command cd -P "$_unresolved_root" > /dev/null && command pwd -P )"
REBUILD_STUFF_DIR="$( command cd -P "$REBUILD_ENV_DIR/../stuff" > /dev/null && command pwd -P )"
REBUILD_SHELL_FRAMEWORK_DIR=$REBUILD_ENV_DIR/framework
export _BES_DEV_ROOT=$REBUILD_SHELL_FRAMEWORK_DIR
_framework_env_dir=$REBUILD_SHELL_FRAMEWORK_DIR/env
if [ -d $_framework_env_dir ]; then
  source $_framework_env_dir/bes_framework.sh
fi
unset _framework_env_dir
unset _this_file
unset _unresolved_root
'''

  _ENV_FILE_TAIL_TEMPLATE = '''\
unset REBUILD_ENV_DIR
unset REBUILD_STUFF_DIR
'''
  
  def _variable_substitution_hook(self, where, installation_dir):
    replacements = {
      '${REBUILD_PACKAGE_PREFIX}': installation_dir,
      '${REBUILD_PACKAGE_NAME}': self.metadata.name,
      '${REBUILD_PACKAGE_DESCRIPTION}': self.metadata.name,
      '${REBUILD_PACKAGE_FULL_VERSION}': str(self.metadata.build_version),
      '${REBUILD_PACKAGE_FULL_NAME}': self.package_descriptor.full_name,
      '#@REBUILD_HEAD@': self._ENV_FILE_HEAD_TEMPLATE,
      '#@REBUILD_TAIL@': self._ENV_FILE_TAIL_TEMPLATE,
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
  def is_package(clazz, tarball):
    'Return True if the given archive is a valid package.'
    # FIXME: Maybe check some more stuff
    return archiver.is_valid(tarball) and archiver.has_member(tarball, clazz.METADATA_FILENAME)

  @classmethod
  def descriptor_cmp(clazz, p1, p2):
    'Compare descriptor and return an int either -1, 0, or 1'
    assert isinstance(p1, package)
    assert isinstance(p2, package)
    return package_descriptor.full_name_cmp(p1.package_descriptor, p2.package_descriptor)

  @classmethod
  def package_files(clazz, tarball):
    return package(tarball).files

  @classmethod
  def create_package(clazz, tarball_path, pkg_desc, build_target, stage_dir, timer = None):
    timer = timer or noop_debug_timer()

    properties = dict_util.filter_without_keys(pkg_desc.properties, [ 'export_compilation_flags_requirements' ])
    
    # Hack the export_compilation_flags_requirements property to be a plain
    # string list instead of the masked config it is
    key = 'export_compilation_flags_requirements'
    if key in pkg_desc.properties:
      properties[key] = [ str(x) for x in pkg_desc.properties[key] ]
      
    files_dir = path.join(stage_dir, 'files')
    timer.start('create_package - find files')
    files = file_find.find(files_dir, relative = True, file_type = file_find.FILE | file_find.LINK)
    timer.stop()
    timer.start('create_package - files checksums')
    files_checksum_list = file_checksum_list.from_files(files, root_dir = files_dir)
    timer.stop()

    env_files_dir = path.join(stage_dir, 'env')
    timer.start('create_package - find env_files')
    if path.isdir(env_files_dir):
      env_files = file_find.find(env_files_dir, relative = True, file_type = file_find.FILE | file_find.LINK)
    else:
      env_files = []
    timer.stop()
    timer.start('create_package - env_files checksums')
    env_files_checksum_list = file_checksum_list.from_files(env_files, root_dir = env_files_dir)
    timer.stop()

    pkg_files = package_files(files_checksum_list, env_files_checksum_list)
    
    metadata = package_metadata('',
                                pkg_desc.name,
                                pkg_desc.version.upstream_version,
                                pkg_desc.version.revision,
                                pkg_desc.version.epoch,
                                build_target.system,
                                build_target.level,
                                build_target.arch,
                                build_target.distro,
                                build_target.distro_version,
                                pkg_desc.requirements,
                                properties,
                                pkg_files)
    metadata_filename = path.join(stage_dir, clazz.METADATA_FILENAME)
    file_util.save(metadata_filename, content = metadata.to_json())
    clazz._create_package(tarball_path, stage_dir, timer)
    return tarball_path, metadata

  @classmethod
  def _determine_manifest(clazz, stage_dir):
    'Return the list of files to package.  Maybe could do some filtering here.  Using find because its faster that bes.fs.file_find.'
    stuff = dir_util.list(stage_dir, relative = True)
    rv = execute.execute([ 'find' ] + stuff + ['-type', 'f' ], cwd = stage_dir)
    files = text_line_parser.parse_lines(rv.stdout, strip_text = True, remove_empties = True)
    rv = execute.execute([ 'find' ] + stuff + ['-type', 'l' ], cwd = stage_dir)
    links = text_line_parser.parse_lines(rv.stdout, strip_text = True, remove_empties = True)
    return sorted(files + links)
  
  @classmethod
  def _create_package(clazz, tarball_filename, stage_dir, timer):
    'Return the list of files to package.  Maybe could do some filtering here.  Using find because its faster that bes.fs.file_find.'
    if timer:
      timer.start('create_package - determine manifest')
    files_to_package = clazz._determine_manifest(stage_dir)
    if timer:
      timer.stop()
    file_util.mkdir(path.dirname(tarball_filename))
    manifest = temp_file.make_temp_file(content = '\n'.join(files_to_package))
    tar_cmd = [ 'tar', 'zcf', tarball_filename, '-C', stage_dir, '-T', manifest ]
    if timer:
      timer.start('create_package - execute %s' % (' '.join(tar_cmd)))
    execute.execute(tar_cmd)
    if timer:
      timer.stop()
  
check.register_class(package, include_seq = False)
