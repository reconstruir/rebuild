#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import requests
from collections import namedtuple

class pcloud_requests(object):

  API = 'https://api.pcloud.com'

  _response = namedtuple('_response', 'url, status_code, payload')
  @classmethod
  def get_to_json(clazz, api_method, params):
    url = self._make_api_url(api_method)
    response = requests.get(url, params = params)
    if response.status_code == 200:
      payload = response.json()
    else:
      payload = None
    return clazz._response(url, response.status_code, payload)

  @classmethod
  def _make_api_url(clazz, method):
    return urljoin(clazz.API, method)
