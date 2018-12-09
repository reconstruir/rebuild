#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path
from bes.url import url_util
from bes.fs import file_util, temp_file
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
  def archive_binary(clazz, executable_filename, archive_filename, arcname):
    'Archive the given the executable_filename into archive_filename and return a tmp file with the result.'
    if not binary_detector.is_executable(executable_filename):
      raise RuntimeError('not an executable: %s' % (executable_filename))
    if not archive_extension.is_valid_filename(archive_filename):
      raise RuntimeError('not a valid archive filename: %s' % (archive_filename))
    if not file_util.is_basename(archive_filename):
      raise RuntimeError('archive_filename should be a filename not a path: %s' % (archive_filename))
    mode = file_util.mode(executable_filename)
    if mode != 0o755:
      raise RuntimeError('mode should be 0755 instead of %s: %s' % (oct(mode), executable_filename))
    empty_dir = temp_file.make_temp_dir()
    tmp_dir = temp_file.make_temp_dir()
    tmp_archive_filename = path.join(tmp_dir, archive_filename)
    arcname = arcname or path.join('bin', path.basename(executable_filename))
    archiver.create(tmp_archive_filename, empty_dir, extra_items = [ archiver.item(executable_filename, arcname) ] )
    file_util.remove(empty_dir)
    return tmp_archive_filename

  @classmethod
  def fix_executable_mode(clazz, executable_filename):
    # if the executable does not have the right mode, make a tmp copy and fix it
    if file_util.mode(executable_filename) == 0o755:
      return None
    tmp_dir = temp_file.make_temp_dir()
    tmp_executable_filename = path.join(tmp_dir, path.basename(executable_filename))
    file_util.copy(executable_filename, tmp_executable_filename)
    os.chmod(tmp_executable_filename, 0o755)
    return tmp_executable_filename
