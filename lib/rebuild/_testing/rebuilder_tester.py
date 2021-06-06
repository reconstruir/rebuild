#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs, os, os.path as path, subprocess, sys
from bes.fs.file_checksum import file_checksum
from bes.fs.file_checksum import file_checksum_list
from bes.fs.file_find import file_find
from bes.fs.temp_file import temp_file
from bes.archive.archiver import archiver
from bes.common.string_util import string_util
from bes.git.git_address_util import git_address_util
from collections import namedtuple
from rebuild.base.build_arch import build_arch
from rebuild.base.build_level import build_level
from rebuild.base.build_system import build_system
from rebuild.base.build_target import build_target

class rebuilder_tester(object):

  class config(namedtuple('config', 'read_contents, read_checksums, build_target, no_network')):

    def __new__(clazz, read_contents = False, read_checksums = False, bt = None, no_network = True):
      bt = bt or build_target.make_host_build_target(level = build_level.RELEASE)
      return clazz.__bases__[0].__new__(clazz, read_contents, read_checksums, bt, no_network)
  
  result = namedtuple('result', 'tmp_dir, command, result, artifacts_dir, artifacts, artifacts_members, artifacts_contents, droppings, checksums, checksums_contents, source_dir_droppings')
  
  def __init__(self, script, working_dir, source_dir, level, debug = False):
    self._script = script
    self._working_dir = working_dir
    self._source_dir = source_dir
    self._level = level
    self._debug = debug

  def _make_temp_dir(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self._debug)
    if self._debug:
      print("tmp_dir: ", tmp_dir)
    return tmp_dir

  def _make_command(self, config, tmp_dir, *args):
    if not  '--storage-config' in args:
      from rebuild.config.storage_config_manager import storage_config_manager
      location = self._source_dir
      content = storage_config_manager.make_local_config_content('unit_test', location, 'rebuild_stuff', None)
      tmp_config = temp_file.make_temp_file(content = content, delete = not self._debug)
      cmd = [
        '--storage-config', tmp_config,
        '--sources-config-name', 'unit_test',
      ]
    else:
      cmd = []
    if config.no_network:
      cmd += [ '--no-network' ]
    cmd += [
      '--verbose',
      '--root', tmp_dir,
#      '--level', self._level,
      '--timestamp', 'timestamp',
    ] + list(args)
    return cmd

  def run(self, config, *args):
    tmp_dir = self._make_temp_dir()
    command = self._make_command(config, tmp_dir, *args)
    artifacts_dir = path.join(tmp_dir, 'artifacts', config.build_target.build_path)
    checksums_dir = path.join(tmp_dir, 'checksums', config.build_target.build_path)
    result = self.run_script(command, cwd = self._working_dir)
    artifacts = self._find_in_dir(artifacts_dir)
    checksums = self._find_in_dir(checksums_dir, patterns = [ '*.checksums' ])
    droppings = self._find_in_dir(tmp_dir)
    source_dir_droppings = self._find_in_dir(self._source_dir)
    
    artifacts_members = {}
    artifacts_contents = {}
    checksums_contents = {}
    if result.exit_code == 0:
      for artifact in artifacts:
        artifact_path = path.join(artifacts_dir, artifact)
        artifacts_members[artifact] = archiver.members(artifact_path)
        if config.read_contents:
          artifacts_contents[artifact] = self._artifact_contents(artifact_path)

      if config.read_checksums:
        checksums_contents = self._load_checksums(config, checksums_dir, tmp_dir, checksums)
          
    if result.exit_code != 0 or self._debug:
      sys.stdout.write(result.stdout)
      sys.stdout.write('\n')
      sys.stdout.flush()
    return self.result(tmp_dir, command, result, artifacts_dir, artifacts, artifacts_members,
                       artifacts_contents, droppings, checksums, checksums_contents,
                       source_dir_droppings)

  @classmethod
  def _find_in_dir(clazz, where, patterns = None):
    if not path.isdir(where):
      return []
    if patterns:
      return file_find.find_fnmatch(where, patterns, file_type = file_find.FILE)
    else:
      return file_find.find(where, file_type = file_find.FILE)
  
  @classmethod
  def _load_checksums(clazz, config, checksums_dir, tmp_dir, checksums):
    checksums_contents = {}
    for checksum in checksums:
      checksum_path = path.join(checksums_dir, checksum)
      from bes.fs.file_util import file_util
      checksums_contents[checksum] = clazz._fix_checksums(config, file_checksum_list.load_checksums_file(checksum_path), tmp_dir)
    return checksums_contents
  
  @classmethod
  def _fix_checksums(clazz, config, checksums, tmp_dir):
    assert not tmp_dir.endswith(path.sep)
    result = file_checksum_list()
    for checksum in checksums:

      long_form = '%s-%s-%s' % (config.build_target.system, config.build_target.distro, config.build_target.distro_version_major)
      short_form = '%s-%s' % (config.build_target.system, config.build_target.distro_version_major)

      replacements = {
        tmp_dir + path.sep: '',
        long_form: '$BUILD_PATH',
        short_form: '$BUILD_PATH',
        git_address_util.sanitize_for_local_path(os.getcwd()): '$WORK_DIR',
        git_address_util.sanitize_for_local_path(path.expanduser('~')): '$HOME',
        '-'.join(sorted(config.build_target.arch)): '$ARCH',
      }
      new_filename = string_util.replace(checksum.filename, replacements, word_boundary = False)
      i = new_filename.rfind('$BUILD_PATH')
      if i > 0:
        new_filename = new_filename[i:]
      fc = file_checksum(new_filename, checksum.checksum)
      result.append(fc)
    return result
  
  @classmethod
  def _blacklist(clazz, member, patterns):
    for pattern in patterns:
      if pattern in member:
        return True
    return False
  
  @classmethod
  def _artifact_contents(clazz, artifact):
    result = {}
    for member in archiver.members(artifact):
      if not clazz._blacklist(member, [ 'bin/rebbe_', 'lib/librebbe_' ]):
        result[member] = archiver.extract_member_to_string(artifact, member).decode('utf8')
    return result

  def make_command(self, args):
    cmd = [ self._script ] + list(args)
    return cmd

  def run_script(self, args, cwd = None, env = None):
    rv = self.run_script_raw(args, cwd = cwd, env = env)
    stdout = rv.stdout.decode('utf-8')
    if rv.exit_code != 0:
      print(rv.stdout)
    return self.exec_result(rv.exit_code, stdout)

  def run_script_raw(self, args, cwd = None, env = None):
    cmd = self.make_command(args)
    return self._exec(cmd, cwd, env)
  
  exec_result = namedtuple('exec_result', 'exit_code,stdout')
  @classmethod
  def _exec(clazz, cmd, cwd, env):
    process = subprocess.Popen(cmd, cwd = cwd, env = env, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = False)
    stdout, _ = process.communicate()
    exit_code = process.wait()
    return clazz.exec_result(exit_code, stdout.strip())
