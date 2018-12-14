#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path
from collections import namedtuple

from bes.common import check
from bes.archive import archiver, archive_extension
from bes.fs import file_util, tar_util, temp_file
from bes.system import execute, log
from bes.url import url_util

from rebuild.binary_format import binary_detector
from rebuild.artifactory.artifactory_requests import artifactory_requests

class ingest_util(object):

  @classmethod
  def download_binary(clazz, url, filename, binary_arc_name):
    'Download a single binary exe and package it into a tarball with sanity checking.'
    if not archive_extension.is_valid_filename(filename):
      raise RuntimeError('filename should be an archive: %s' % (filename))
    tmp = url_util.download_to_temp_file(url)
    if not binary_detector.is_executable(tmp):
      file_util.remove(tmp)
      raise RuntimeError('not an executable: %s' % (url))
    os.chmod(tmp, 0o755)
    empty_dir = temp_file.make_temp_dir()
    archiver.create(filename, empty_dir, extra_items = [ archiver.item(tmp, binary_arc_name) ] )
    file_util.remove(tmp)
    
  @classmethod
  def download_archive(clazz, url, filename = None):
    'Download an archive with sanity checking it is indeed a valid tarball type.'
    filename = filename or url_util.url_path_baename(url)
    if not archive_extension.is_valid_filename(filename):
      raise RuntimeError('filename should be a valid archive name.')
    tmp_dir = temp_file.make_temp_dir()
    tmp = path.join(tmp_dir, filename)
    url_util.download_to_file(url, tmp)
    if not archiver.is_valid(tmp):
      file_util.remove(tmp)
      raise RuntimeError('not a valid archive: %s' % (url))
    os.chmod(tmp, 0o644)
    file_util.rename(tmp, filename)

  @classmethod
  def archive_binary(clazz, executable_filename, archive_filename, arcname, debug = False):
    'Archive the given the executable_filename into archive_filename and return a tmp file with the result.'
    if not binary_detector.is_executable(executable_filename):
      raise RuntimeError('not an executable: %s' % (executable_filename))
    if not archive_extension.is_valid_filename(archive_filename):
      raise RuntimeError('not a valid archive filename: %s' % (archive_filename))
    if not file_util.is_basename(archive_filename):
      raise RuntimeError('archive_filename should be a filename not a path: %s' % (archive_filename))
    tar_dir = temp_file.make_temp_dir(delete = False)
    arcname = arcname or path.join('bin', path.basename(executable_filename))
    dst_file = path.join(tar_dir, arcname)
    file_util.copy(executable_filename, dst_file)
    os.chmod(dst_file, 0o755)
    tmp_dir = temp_file.make_temp_dir(delete = not debug)
    tmp_archive_filename = path.join(tmp_dir, archive_filename)
    tar_util.create_deterministic_tarball(tmp_archive_filename, tar_dir, arcname, '2018-12-08')
    file_util.remove(tar_dir)
    return tmp_archive_filename

  @classmethod
  def fix_executable(clazz, executable_filename, debug = False):
    '''
    Fix the mode, atime and mtime of an executable so when it is included in a tarball
    the checksum will be deterministic.
    '''
    tmp_dir = temp_file.make_temp_dir(delete = not debug)
    tmp_executable_filename = path.join(tmp_dir, path.basename(executable_filename))
    file_util.copy(executable_filename, tmp_executable_filename)
    os.chmod(tmp_executable_filename, 0o755)
    os.utime(tmp_executable_filename, ( 1544487203, 1544486779 )) # a random date on 12/2018
    return tmp_executable_filename

  _ingest_result = namedtuple('_ingest_result', 'success, reason')
  
  @classmethod
  def ingest_url(clazz, url, remote_filename, arcname, checksum, storage, dry_run = False, debug = False):
    check.check_string(url)
    check.check_string(remote_filename)
    if arcname:
      check.check_string(arcname)
    if checksum:
      check.check_string(checksum)
    clazz.log_d('ingest_url: url=%s; arcname=%s' % (url, arcname))
    local_filename = url_util.download_to_temp_file(url, basename = 'tmp_download_for_ingest')
    clazz.log_d('ingest_url: downloaded remote url %s => %s' % (url, local_filename))
    if checksum:
      local_checksum = file_util.checksum('sha256', local_filename)
      if local_checksum != checksum:
        return clazz._ingest_result(False, 'failed: url checksum does not match: %s' % (url))
    properties = { 'rebuild.ingestion_url': url }
    return clazz.ingest_file(local_filename, remote_filename, arcname, storage,
                             properties = properties, dry_run = dry_run, debug = debug)
                     
  @classmethod
  def ingest_file(clazz, local_filename, remote_filename, arcname, storage, properties = {}, dry_run = False, debug = False):
    check.check_string(local_filename)
    check.check_string(remote_filename)
    if arcname:
      check.check_string(arcname)
    if properties:
      check.check_dict(properties)
    clazz.log_d('ingest_file: local_filename=%s; remote_filename=%s; arcname=%s; storage=%s' % (local_filename,
                                                                                                remote_filename,
                                                                                                arcname,
                                                                                                str(storage)))
    if not path.isfile(local_filename):
      return clazz._ingest_result(False, 'file not found: %s' % (local_filename))

    remote_basename = path.basename(remote_filename)
    
    is_valid_archive = archiver.is_valid(local_filename)
    is_exe = binary_detector.is_executable(local_filename)
    clazz.log_d('ingest_file: is_valid_archive=%s; is_exe=%s' % (is_valid_archive, is_exe))
    if not (is_valid_archive or is_exe):
      return clazz._ingest_result(False, 'content to ingest should be an archive or executable: %s' % (local_filename))

    tmp_files_to_cleanup = []
    def _cleanup_tmp_files():
      if not debug:
        file_util.remove(tmp_files_to_cleanup)

    # if local_filename is an executable, archive into a tarball first
    if is_exe:
      local_filename = clazz.fix_executable(local_filename, debug = debug)
      clazz.log_d('ingest_file: fixed executable: %s' % (local_filename))
      tmp_files_to_cleanup.append(local_filename)
      clazz.log_d('ingest_file: calling archive_binary(%s, %s, %s)' % (local_filename, remote_basename, arcname))
      local_filename = clazz.archive_binary(local_filename, remote_basename, arcname, debug = debug)
      clazz.log_d('ingest_file: calling archive_binary() returns %s' % (local_filename))
      tmp_files_to_cleanup.append(local_filename)

    remote_path = storage.remote_filename_abs(remote_filename)
    remote_checksum = storage.remote_checksum(remote_filename)
    local_checksum = file_util.checksum('sha1', local_filename)
    clazz.log_d('ingest_file: remote_path=%s; remote_checksum=%s; local_checksum=%s' % (remote_path, remote_checksum, local_checksum))
    if remote_checksum == local_checksum:
      _cleanup_tmp_files()
      return clazz._ingest_result(True, 'a file with checksum %s already exists: %s' % (local_checksum, remote_path))
    if remote_checksum is not None and remote_checksum != local_checksum:
      _cleanup_tmp_files()
      msg = '''trying to re-ingest a with a different checksum.
 local_filename: %s
 local_checksum: %s
remote_checksum: %s''' % (local_filename, local_checksum, remote_checksum)
      return clazz._ingest_result(True, msg)
    if dry_run:
      return clazz._ingest_result(True, 'dry-run: would upload %s => %s' % (local_filename, remote_path))
    
    try:
      clazz.log_d('ingest_file() calling upload(%s, %s)' % (local_filename, remote_path))
      rv = storage.upload(local_filename, remote_path, local_checksum)
      clazz.log_d('ingest_file() rv=%s - %s' % (rv, type(rv)))
      if rv:
        ingested_address = storage.make_address().mutate_filename(remote_filename)
        username = storage._config.upload_credentials.credentials.username
        password = storage._config.upload_credentials.credentials.password
        properties_rv = artifactory_requests.set_properties(ingested_address, properties, username, password)
        if not properties_rv:
          return clazz._ingest_result(False, 'Failed to set properties.  Something went wrong.  FIXME: should delete the remote file.')
      else:
        return clazz._ingest_result(False, 'Failed to upload.  Something went wrong.  FIXME: should delete the remote file.')
    finally:
      _cleanup_tmp_files()
      
    return clazz._ingest_result(True, 'successfully ingested %s' % (local_filename))
  
log.add_logging(ingest_util, 'ingest_util')
