#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.compat import StringIO
from bes.common import check, cached_property
from bes.fs import file_util

class artifactory_address(namedtuple('artifactory_address', 'hostname, repo, root_dir, sub_repo, filename')):

  def __new__(clazz, hostname, repo, root_dir, sub_repo, filename):
    check.check_string(hostname)
    hostname = clazz._normalize_hostname(hostname)
    check.check_string(repo)
    repo = clazz._normalize_path(repo)
    root_dir = clazz._normalize_path(root_dir)
    if sub_repo is not None:
      check.check_string(sub_repo)
      sub_repo = clazz._normalize_path(sub_repo)
    if filename is not None:
      check.check_string(filename)
      filename = clazz._normalize_path(filename)
    return clazz.__bases__[0].__new__(clazz, hostname, repo, root_dir, sub_repo, filename)

  @classmethod
  def _normalize_hostname(clazz, hostname):
    if not hostname.endswith('/'):
      return hostname + '/'
    return hostname
  
  @classmethod
  def _normalize_path(clazz, filename):
    return file_util.strip_sep(filename)
  
  def __str__(self):
    return self.url

  @cached_property
  def url(self):
    buf = StringIO()
    buf.write(self.hostname)
    buf.write(self.repo)
    buf.write('/')
    buf.write(self.root_dir)
    if self.sub_repo:
      buf.write('/')
      buf.write(self.sub_repo)
    if self.filename:
      buf.write('/')
      buf.write(self.filename)
    return buf.getvalue()

  @cached_property
  def api_url(self):
    return '{hostname}api'.format(hostname = self.hostname)

  @cached_property
  def search_aql_url(self):
    return '{api_url}/search/aql'.format(api_url = self.api_url)

  def mutate_filename(self, filename):
    index = self._fields.index('filename')
    l = list(self)
    l[index] = filename
    return self.__class__(*l)
  
check.register_class(artifactory_address)
