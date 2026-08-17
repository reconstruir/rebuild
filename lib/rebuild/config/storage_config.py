#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple

from bes.system.check import check
from bes.property.cached_property import cached_property
from bes.property.env_var_property import env_var_property
from bes.system.log import logger

from bsecret.credentials.credentials import credentials

from .storage_config_error import storage_config_error

class storage_config(namedtuple('storage_config', 'name, provider, location, repo, root_dir, download, upload')):

  log = logger('storage_config')
  
  def __init__(self, name, provider, location, repo, root_dir, download, upload):
    check.check_string(name)
    check.check_string(provider)
    check.check_string(location, allow_none = True)
    check.check_string(repo, allow_none = True)
    check.check_string(root_dir, allow_none = True)
    check.check_credentials(download)
    check.check_credentials(upload)
    self._name = name
    self._provider = provider
    self._location = location
    self._repo = repo
    self._root_dir = root_dir
    self._upload = upload
    self._download = download

  @env_var_property
  def name(self):
    return self._name

  @env_var_property
  def provider(self):
    return self._provider
  
  @env_var_property
  def location(self):
    return self._location
  
  @env_var_property
  def repo(self):
    return self._repo
  
  @env_var_property
  def root_dir(self):
    return self._root_dir
  
  @property
  def download(self):
    return self._download
  
  @property
  def upload(self):
    return self._upload
  
  @classmethod
  def create_from_config(clazz, source, values):
    check.check_dict(values)
    if 'name' not in values:
      raise storage_config_error('"name" entry not found')
    if 'provider' not in values:
      raise storage_config_error('"provider" entry not found')
    name = values['name']
    provider = values['provider']
    location = values.get('location')
    repo = values.get('repo')
    root_dir = values.get('root_dir')
    download_username = values.get('download_username') or ''
    download_password = values.get('download_password') or ''
    upload_username = values.get('upload_username') or ''
    upload_password = values.get('upload_password') or ''
    download = credentials(source)
    download.username = download_username
    download.password = download_password
    upload = credentials(source)
    upload.username = upload_username
    upload.password = upload_password
    return storage_config(name, provider, location, repo, root_dir, download, upload)

  @cached_property
  def full_path(self):
    parts = [ self.location ]
    if self.repo:
      parts.append(self.repo)
    if self.root_dir:
      parts.append(self.root_dir)
    return path.join(*parts)
  
check.register_class(storage_config, include_seq = False)
