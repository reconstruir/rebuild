#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path

from bes.archive import archiver
from bes.fs import file_checksum_list, file_find

from .tarball_finder import tarball_finder
from .source_finder_db_entry import source_finder_db_entry

class source_tool(object):

  @classmethod
  def find_sources(clazz, directory):
    files = file_find.find(directory, relative = True, file_type = file_find.FILE | file_find.LINK)
    sources = []
    for f in files:
      if archiver.is_valid(path.join(directory, f)):
        sources.append(f)
    return sources
  
  @classmethod
  def update_sources_index(clazz, directory):
    sources = clazz.find_sources(directory)
    checksums = file_checksum_list.from_files(sources, root_dir = directory, function_name = 'sha1')
    checksums.save_checksums_file(path.join(directory, 'sources_index.json'))
    return 0
