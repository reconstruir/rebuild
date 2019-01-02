#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common import check

from .credentials import credentials

class storage_config(namedtuple('storage_config', 'name, provider, location, repo, root_dir, download, upload')):

  def __new__(clazz, name, provider, location, repo, root_dir, download, upload):
    check.check_string(name)
    check.check_string(provider)
    check.check_string(location, allow_none = True)
    check.check_string(repo)
    check.check_string(root_dir, allow_none = True)
    check.check_credentials(download)
    check.check_credentials(upload)
    return clazz.__bases__[0].__new__(clazz, name, provider, location, repo, root_dir, download, upload)

  @classmethod
  def create_from_config(clazz, section):
    check.check_config_section(section)
    name = section.find_by_key('name')
    provider = section.find_by_key('provider')
    location = section.find_by_key('location', raise_error = False)
    repo = section.find_by_key('repo')
    root_dir = section.find_by_key('root_dir', raise_error = False)
    download_username = section.find_by_key('download.username', raise_error = False) or ''
    download_password = section.find_by_key('download.password', raise_error = False) or ''
    upload_username = section.find_by_key('upload.username', raise_error = False) or ''
    upload_password = section.find_by_key('upload.password', raise_error = False) or ''
    download = credentials(download_username, download_password)
    upload = credentials(upload_username, upload_password)
    return storage_config(name, provider, location, repo, root_dir, download, upload)

check.register_class(storage_config, include_seq = False)
