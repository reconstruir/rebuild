#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from rebuild.storage.storage_address import storage_address

from bes.system.check import check

class artifactory_address(object):

  @classmethod
  def make_search_aql_url(clazz, address):
    check.check_storage_address(address)
    return '{api_url}/search/aql'.format(api_url = clazz.make_api_url(address))

  @classmethod
  def make_api_url(clazz, address, endpoint = None, file_path = None, params = None):
    check.check_storage_address(address)
    
    if endpoint:
      api_url = '{hostname}api/{endpoint}'.format(hostname = address.hostname, endpoint = endpoint)
    else:
      api_url = '{hostname}api'.format(hostname = address.hostname)

    if file_path:
      url = '{api_url}/{file_path}'.format(api_url = api_url, file_path = file_path)
    else:
      url = api_url
      
    if params:
      url = '{url}?{params}'.format(url = url, params = params)
      
    return url
