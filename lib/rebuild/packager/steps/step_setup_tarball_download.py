#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-


import os.path as path

#from bes.archive import archiver
from rebuild.step_manager import Step, step_result
from rebuild import build_blurb #, TarballUtil
#from bes.common import object_util, dict_util
#from bes.fs import file_util
from rebuild.git import Git
from bes.common import time_util

class step_setup_tarball_download(Step):
  'Download a tarball.'

  def __init__(self):
    super(step_setup_tarball_download, self).__init__()

  def execute(self, argument):
#    print "FUCK step_setup_tarball_download.execute - %s" % (argument.env.package_info.full_name)
#    tarball_address = argument.args.get('tarball_address', None)
#    print "FUCK: ", tarball_address
#    if tarball_address:
#      print "FUCK: ", tarball_address
    return step_result(True, None)

  def sources_keys(self):
    return [ 'tarballs' ]

  @classmethod
  def parse_step_args(clazz, packager_env, args):
    pd = packager_env.package_descriptor
    tarball_address = args.get('tarball_address', None)
    if tarball_address:
      timestamp = time_util.timestamp(delimiter = '.', milliseconds = False)
      basename = '%s-%s-%s.tar.gz' % (pd.name, pd.version, timestamp)
      filename = path.join(packager_env.download_dir, basename)
      Git.download_tarball(pd.name, 'HEAD', tarball_address, filename)
      print "FUCK: downloaded: ", filename
    return {}
