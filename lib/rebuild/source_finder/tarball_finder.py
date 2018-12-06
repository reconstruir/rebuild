#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, re
from bes.fs import file_find

class tarball_finder(object):

  @classmethod
  def find_by_filename(self, where, filename):
    tarballs = file_find.find_fnmatch(where, [ filename ], max_depth = 4, relative = False, file_type = file_find.FILE | file_find.LINK)
    if not tarballs:
      return None
    if len(tarballs) == 1:
      return tarballs[0]
    else:
      raise RuntimeError('Too many tarballs found for %s' % (filename))
