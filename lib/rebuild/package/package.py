#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, re

from collections import namedtuple

from bes.archive import archive, archiver
from bes.common import check, dict_util, json_util, string_util
from bes.fs import dir_util, file_check, file_find, file_mime, file_search, file_replace, file_util, tar_util, temp_file
from bes.text import text_line_parser
from bes.match import matcher_filename, matcher_multiple_filename
from bes.python import setup_tools
from bes.system import execute, log
from rebuild.base import build_blurb, build_target, package_descriptor
from bes.debug import debug_timer

from .package_metadata import package_metadata
from .package_manifest import package_manifest
from .package_file_list import package_file_list

class package(object):

  METADATA_DIR = 'metadata'
  METADATA_FILENAME = METADATA_DIR + '/' + 'metadata.json'
  FILES_DIR = 'files'
  ENV_DIR = 'env'

  def __init__(self, tarball):
    log.add_logging(self, 'package')
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
    return self.metadata.manifest.files.filenames()

  def extract(self, root_dir, stuff_dir_basename, env_dir_basename):
    tmp_dir = temp_file.make_temp_dir(prefix = 'package.extract.', suffix = '.dir', dir = root_dir)
    dst_stuff_dir = path.join(root_dir, stuff_dir_basename)
    dst_env_dir = path.join(root_dir, env_dir_basename)
    file_util.mkdir(dst_stuff_dir)
    file_util.mkdir(dst_env_dir)
    # tar cmd is 10x faster than archiver.  need to fix archiver
    tar_cmd = [ 'tar', 'xf', self.tarball, '-C', tmp_dir ]
    execute.execute(tar_cmd)
    src_stuff_dir = path.join(tmp_dir, self.FILES_DIR)
    src_env_dir = path.join(tmp_dir, self.ENV_DIR)
    if path.isdir(src_stuff_dir):
      dir_util.move_files(src_stuff_dir, dst_stuff_dir)
    self._update_python_config_files(dst_stuff_dir)
    self._replace_variables_files(dst_stuff_dir, dst_stuff_dir)
    if path.isdir(src_env_dir):
      dir_util.move_files(src_env_dir, dst_env_dir)
    self._replace_variables_env_files(dst_env_dir, dst_stuff_dir)
    file_util.remove(tmp_dir)
      
  def _update_python_config_files(self, stuff_dir):
    python_lib_dir = path.join(stuff_dir, 'lib/python')
    setup_tools.update_egg_directory(python_lib_dir)

  _ENV_FILE_HEAD_TEMPLATE = '''\
# BEGIN @REBUILD_HEAD@
_this_file="$( command readlink "$BASH_SOURCE" )" || _this_file="$BASH_SOURCE"
_unresolved_root="${_this_file%/*}"
REBUILD_ENV_DIR="$( command cd -P "$_unresolved_root" > /dev/null && command pwd -P )"
REBUILD_STUFF_DIR="$( command cd -P "$REBUILD_ENV_DIR/../stuff" > /dev/null && command pwd -P )"
REBUILD_SHELL_FRAMEWORK_DIR=$REBUILD_ENV_DIR/framework
export _REBUILD_DEV_ROOT=$REBUILD_SHELL_FRAMEWORK_DIR

if [ -d $REBUILD_SHELL_FRAMEWORK_DIR ]; then
  source $REBUILD_SHELL_FRAMEWORK_DIR/rebuild_framework.sh
fi
unset _this_file
unset _unresolved_root
# END @REBUILD_HEAD@

'''

  _ENV_FILE_TAIL_TEMPLATE = '''\

# BEGIN @REBUILD_TAIL@
unset REBUILD_ENV_DIR
unset REBUILD_STUFF_DIR
# END @REBUILD_TAIL@

'''
  
  def _replace_variables_files(self, where, stuff_dir):
    files = self.metadata.manifest.files.files_with_hardcoded_paths()
    replacements = {
      '${REBUILD_PACKAGE_PREFIX}': stuff_dir,
    }
    self.log_d('replacements=%s' % (replacements))
    for f in files:
      filename = path.join(stuff_dir, f)
      self.log_d('doing replacements for: %s' % (path.relpath(filename)))
      file_replace.replace(filename, replacements, backup = False, word_boundary = True)
  
  def _replace_variables_env_files(self, where, stuff_dir):
    replacements = {
      '${REBUILD_PACKAGE_PREFIX}': stuff_dir,
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
  def package_manifest(clazz, tarball):
    return package(tarball).files

  _create_package_result = namedtuple('_create_package_result', 'filename, metadata')
  @classmethod
  def create_package(clazz, tarball_path, pkg_desc, build_target, stage_dir,
                     timer = None):
    timer = timer or debug_timer('package', disabled = True)

    properties = dict_util.filter_without_keys(pkg_desc.properties, [ 'export_compilation_flags_requirements' ])
    
    # Hack the export_compilation_flags_requirements property to be a plain
    # string list instead of the masked config it is
    key = 'export_compilation_flags_requirements'
    if key in pkg_desc.properties:
      properties[key] = [ str(x) for x in pkg_desc.properties[key] ]
      
    stage_files_dir = path.join(stage_dir, 'files')
    timer.start('create_package - find files')

    # Now find all files that have such a replacement variable
    # Note this could be both files we did in the previous file_search
    # as well as other done independently. *.pc files for example
    files_with_hardcoded_paths = clazz._find_files_with_hardcoded_paths(stage_files_dir)

    if path.isdir(stage_files_dir):
      files = file_find.find(stage_files_dir, relative = True, file_type = file_find.FILE | file_find.LINK)
    else:
      files = []

    timer.stop()
    timer.start('create_package - files checksums')
    stage_package_file_list = package_file_list.from_files(files, files_with_hardcoded_paths, root_dir = stage_files_dir)
    timer.stop()

    stage_env_files_dir = path.join(stage_dir, 'env')
    timer.start('create_package - find env_files')
    if path.isdir(stage_env_files_dir):
      stage_env_files = file_find.find(stage_env_files_dir, relative = True, file_type = file_find.FILE | file_find.LINK)
    else:
      stage_env_files = []
    timer.stop()
    timer.start('create_package - env_files checksums')
    stage_env_package_file_list = package_file_list.from_files(stage_env_files, set(), root_dir = stage_env_files_dir)
    timer.stop()

    pkg_files = package_manifest(stage_package_file_list, stage_env_package_file_list)
    
    # filename is empty cause it only gets filled once metadata ends up in a db
    metadata = package_metadata(package_metadata.FORMAT_VERSION,
                                '',
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
    return clazz._create_package_result(tarball_path, metadata)

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
  def _find_files_with_hardcoded_paths(clazz, where):
    if not path.isdir(where):
      return set()
    found = file_search.search(where, '${REBUILD_PACKAGE_PREFIX}', relative = True)
    return set([ item.filename for item in found ])
  
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
    if timer:
      timer.start('create_package - creating tarball %s' % (tarball_filename))
    tar_util.create_deterministic_tarball_with_manifest(tarball_filename,
                                                        stage_dir,
                                                        manifest,
                                                        '2018-12-08')
    if timer:
      timer.stop()
  
check.register_class(package, include_seq = False)
