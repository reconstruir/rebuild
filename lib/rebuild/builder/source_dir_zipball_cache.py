#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check
from bes.system import execute
from bes.fs import file_util

from bes.git import git_util

class source_dir_zipball_cache(object):

  def __init__(self, root_dir):
    self.root_dir = root_dir

  def get_tarball(self, d):
    if not path.isabs(d):
      d = path.abspath(d)
    zip_filename = self.get_tarball_filename(d)
    file_util.mkdir(path.dirname(zip_filename))
    cmd = [ 'zip', '-x', '*.git*', '-u', '-r', zip_filename, path.basename(d) ]
    rv = execute.execute(cmd, cwd = path.dirname(d), raise_error = False)
    # 12 if the success exit code for zip when update has no work to do
    if rv.exit_code not in [ 0, 12 ]:
      ex = RuntimeError(rv.stdout)
      setattr(ex, 'execute_result', rv)
      print(rv.stdout)
      print(rv.stderr)
      print(str(ex))
      raise ex
    return zip_filename
  
  def get_tarball_filename(self, d):
    assert path.isabs(d)
    dirname = path.dirname(d)
    basename = path.basename(d)
    filename = '%s.zip' % (basename)
    return path.join(self.root_dir, git_util.sanitize_address(dirname), filename)
  
check.register_class(source_dir_zipball_cache, include_seq = False)
