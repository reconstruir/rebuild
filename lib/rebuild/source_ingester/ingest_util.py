#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path
from bes.system import execute
from bes.url import url_util
from bes.fs import file_util, tar_util, temp_file
from bes.archive import archiver, archive_extension
from rebuild.binary_format import binary_detector

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
    gnu_tar = tar_util.find_tar_in_env_path('gnu')
    if not gnu_tar:
      msg = '''you need gnu tar in your path to archive the binary.
bsd tar does not have support for archiving with deterministic checksums for the same binary.'''
      raise RuntimeError(msg)
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
    template = '{tar_exe} --mtime=2018-12-08 -cf - {arcname} | gzip -n > {filename}'
    cmd = template.format(tar_exe = gnu_tar, arcname = arcname, filename = tmp_archive_filename)
#    cmd = '%s --mtime=2018-12-08 -cf - %s | gzip -n > %s' % (arcname, tmp_archive_filename)
#    cmd = '/Users/ramiro/cacatar --mtime=2018-12-10 -cf - %s | gzip -n > %s' % (arcname, tmp_archive_filename)
#    cmd = 'tar --options "mtree:!all" -cf - %s | gzip -n > %s' % (arcname, tmp_archive_filename)
    #cmd = '/Users/ramiro/cacatar --mtime=2018-12-10 -cf - %s | gzip -n > %s' % (arcname, tmp_archive_filename)
    execute.execute(cmd, cwd = tar_dir, shell = True)
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
    os.utime(tmp_executable_filename, ( 1544487203, 1544486779 ))
    return tmp_executable_filename
