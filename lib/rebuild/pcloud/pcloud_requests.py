#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
from collections import namedtuple

from bes.compat.url_compat import urljoin
from bes.url.url_util import url_util

class pcloud_requests(object):

  API = 'https://api.pcloud.com'

  _response = namedtuple('_response', 'url, status_code, payload')
  
  @classmethod
  def get(clazz, api_method, params):
    url = clazz.make_api_url(api_method)
    response = url_util.get(url, params = params)
    if response.status_code == 200:
      payload = json.loads(response.content)
    else:
      payload = None
    return clazz._response(url, response.status_code, payload)

  @classmethod
  def download_to_stream(clazz, links, stream):
    url = 'https://{host}{path}'.format(host = links.hosts[0], path = links.path)
    status_code = url_util.download_to_stream(url, stream)
    return clazz._response(url, status_code, None)

  @classmethod
  def make_api_url(clazz, method):
    return urljoin(clazz.API, method)
