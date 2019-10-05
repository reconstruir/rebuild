#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, re

from collections import namedtuple

from bes.archive.archive import archive
from bes.archive.archiver import archiver
from bes.common.check import check
from bes.common.dict_util import dict_util
from bes.common.json_util import json_util
from bes.common.string_util import string_util
from bes.debug.debug_timer import debug_timer
from bes.fs.file_check import file_check
from bes.fs.file_copy import file_copy
from bes.fs.file_find import file_find
from bes.fs.file_replace import file_replace
from bes.fs.file_search import file_search
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.match.matcher_filename import matcher_filename, matcher_multiple_filename
from bes.property.cached_property import cached_property
from bes.python.setup_tools import setup_tools
from bes.system.execute import execute
from bes.system.log import log
from rebuild.base.build_blurb import build_blurb
from rebuild.base.build_target import build_target
from rebuild.base.package_descriptor import package_descriptor

from rebuild.binary_format.binary_detector import binary_detector

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

  @cached_property
  def metadata(self):
    return package_metadata.parse_json(self.raw_metadata)

  @cached_property
  def raw_metadata(self):
    # FIXME: restore the cache
    #content = archiver.extract_member_to_string_cached(self.tarball, self.METADATA_FILENAME)
    content = archiver.extract_member_to_string(self.tarball, self.METADATA_FILENAME)
    return content.decode('utf-8')
  
  @cached_property
  def package_descriptor(self):
    return self.metadata.package_descriptor

  @cached_property
  def artifact_descriptor(self):
    return self.metadata.artifact_descriptor

  @cached_property
  def system(self):
    return self.metadata.system

  @cached_property
  def build_target(self):
    return self.metadata.build_target

  @cached_property
  def files(self):
    return self.metadata.manifest.files.filenames()

  @cached_property
  def checksums(self):
    return self.metadata.manifest.files.checksums()

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
      file_copy.move_files(src_stuff_dir, dst_stuff_dir)
    self._update_python_config_files(dst_stuff_dir)
    self._replace_variables_files(self.metadata.manifest.files.files_with_hardcoded_paths(),
                                  dst_stuff_dir, dst_stuff_dir)
    if path.isdir(src_env_dir):
      file_copy.move_files(src_env_dir, dst_env_dir)
    self._replace_variables_env_files(self.metadata.manifest.env_files.files_with_hardcoded_paths(),
                                  dst_env_dir, dst_stuff_dir)
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
  source $REBUILD_SHELL_FRAMEWORK_DIR/bes_shell.sh
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

  _ENV_FILE_REPLACEMENT_VARIABLES = [
    '${REBUILD_PACKAGE_PREFIX}',
    '${REBUILD_PACKAGE_FULL_VERSION}',
    '${REBUILD_PACKAGE_FULL_NAME}',
    '#@REBUILD_HEAD@',
    '#@REBUILD_TAIL@',
  ]
  
  def _replace_variables_files(self, files, where, stuff_dir):
    self.log_d('_replace_variables_files: files=%s; where=%s; stuff_dir=%s' % (files, where, stuff_dir))
    replacements = {
      '${REBUILD_PACKAGE_PREFIX}': stuff_dir,
    }
    self.log_d('replacements=%s' % (replacements))
    for f in files:
      filename = path.join(where, f)
      self.log_d('doing replacements for: %s' % (path.relpath(filename)))
      file_replace.replace(filename, replacements, backup = False, word_boundary = True)
  
  def _replace_variables_env_files(self, files, where, stuff_dir):
    self.log_d('_replace_variables_env_files: files=%s; where=%s; stuff_dir=%s' % (files, where, stuff_dir))
    replacements = {
      '${REBUILD_PACKAGE_PREFIX}': stuff_dir,
      '${REBUILD_PACKAGE_FULL_VERSION}': str(self.metadata.build_version),
      '${REBUILD_PACKAGE_FULL_NAME}': self.package_descriptor.full_name,
      '#@REBUILD_HEAD@': self._ENV_FILE_HEAD_TEMPLATE,
      '#@REBUILD_TAIL@': self._ENV_FILE_TAIL_TEMPLATE,
    }
    self.log_d('replacements=%s' % (replacements))
    for f in files:
      filename = path.join(where, f)
      self.log_d('doing replacements for: %s' % (path.relpath(filename)))
      file_replace.replace(filename, replacements, backup = False, word_boundary = True)
  
  @cached_property
  def pkg_config_files(self):
    return matcher_filename('*.pc').filter(self.files)

  @cached_property
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
    stage_package_file_list = package_file_list.from_files(files,
                                                           files_with_hardcoded_paths,
                                                           root_dir = stage_files_dir)
    timer.stop()

    stage_env_files_dir = path.join(stage_dir, 'env')
    env_files_with_hardcoded_paths = clazz._find_env_files_with_variables_paths(stage_env_files_dir)
    timer.start('create_package - find env_files')
    if path.isdir(stage_env_files_dir):
      stage_env_files = file_find.find(stage_env_files_dir, relative = True, file_type = file_find.FILE | file_find.LINK)
    else:
      stage_env_files = []
    timer.stop()
    timer.start('create_package - env_files checksums')
    stage_env_package_file_list = package_file_list.from_files(stage_env_files,
                                                               env_files_with_hardcoded_paths,
                                                               root_dir = stage_env_files_dir)
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
                                build_target.distro_version_major,
                                build_target.distro_version_minor,
                                pkg_desc.requirements,
                                properties,
                                pkg_files)
    metadata_filename = path.join(stage_dir, clazz.METADATA_FILENAME)
    file_util.save(metadata_filename, content = metadata.to_json())
    clazz._create_package(tarball_path, stage_dir, timer)
    return clazz._create_package_result(tarball_path, metadata)

  @classmethod
  def _find_files_with_hardcoded_paths(clazz, where):
    if not path.isdir(where):
      return set()
    found = file_search.search(where, '${REBUILD_PACKAGE_PREFIX}', relative = True)
    return set([ item.filename for item in found ])
  
  @classmethod
  def _find_env_files_with_variables_paths(clazz, where):
    if not path.isdir(where):
      return set()
    found = []
    for s in clazz._ENV_FILE_REPLACEMENT_VARIABLES:
      found += file_search.search(where, s, relative = True)
    return set([ item.filename for item in found ])
  
  @classmethod
  def _create_package(clazz, tarball_filename, stage_dir, timer):
    'Create the package.'
    if timer:
      timer.start('create_package - determine manifest')
    files_to_package = package_manifest.determine_files(stage_dir)
    if timer:
      timer.stop()
    file_util.mkdir(path.dirname(tarball_filename))
    manifest = temp_file.make_temp_file(content = '\n'.join(files_to_package))
    if timer:
      timer.start('create_package - creating tarball %s' % (tarball_filename))
    clazz._prepare_stage_dir(stage_dir, files_to_package)
    clazz._create_tarball(tarball_filename, stage_dir)
    if timer:
      timer.stop()

  @classmethod
  def mutate_metadata(clazz, src, dst, mutations = None, backup = True, fail_on_binaries = True):
    'Mutate the metadata of a package and save a new one.  src and dst can be the same.'
    tmp_dir = temp_file.make_temp_dir(prefix = 'package.mutate_metadata.', suffix = '.dir')
    archiver.extract_all(src, tmp_dir)
    if fail_on_binaries:
      files = file_find.find(tmp_dir, relative = False)
      binary_files = [ f for f in files if binary_detector.is_binary(f) ]
      if len(binary_files) > 0:
        return False
    src_metadata_filename = path.join(tmp_dir, clazz.METADATA_FILENAME)
    src_metadata_json = file_util.read(src_metadata_filename)
    src_metadata = package_metadata.parse_json(src_metadata_json)

    dst_metadata = src_metadata.clone(mutations = mutations)
    dst_metadata_json = dst_metadata.to_json()
    file_util.save(src_metadata_filename, content = dst_metadata_json)
    tmp_dst_archive = temp_file.make_temp_file(suffix = '.tar.gz')
    archiver.create(tmp_dst_archive, tmp_dir)
    if src == dst and backup:
      file_util.backup(src)
    file_util.rename(tmp_dst_archive, dst)
    return True

  @classmethod
  def _prepare_stage_dir(clazz, stage_dir, files_to_package):
    'Prepare the stage dir for packaging.  Remove some stuff that should not be in the package.'
    file_util.remove(path.join(stage_dir, 'files/lib/python/__pycache__/site.cpython-37.pyc'))
    return
    all_files = set(file_find.find(stage_dir, relative = True, file_type = file_find.FILE | file_find.LINK | file_find.DEVICE))
    files_to_package = set(files_to_package)
    to_remove = all_files - files_to_package
    file_util.remove(to_remove)
  
  @classmethod
  def _create_tarball(clazz, filename, stage_dir):
    'Create the tarball.'
    archiver.create(filename, stage_dir, extension = 'tar.gz')
    
  @classmethod
  def _create_tarball_deterministic(clazz, filename, stage_dir, files):
    '''Attempt to create a tarball with a deterministic checksum
    by hardcoding the timestamp.  It doesn't work and needs more 
    research.  The dilemma is that tarball checksums are different 
    depending on the creation checksums of the contents.
    '''
    from bes.fs.tar_util import tar_util
    file_util.mkdir(path.dirname(filename))
    manifest = temp_file.make_temp_file(content = '\n'.join(files))
    tar_util.create_deterministic_tarball_with_manifest(filename,
                                                        stage_dir,
                                                        manifest,
                                                        '2018-12-08')
  
    
check.register_class(package, include_seq = False)
