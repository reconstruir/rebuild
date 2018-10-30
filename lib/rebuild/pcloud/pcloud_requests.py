#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, urllib

from bes.system import compat

if compat.IS_PYTHON2:
  from urllib2 import urlopen, Request
  from urllib import urlencode
else:
  from urllib.request import urlopen, Request
  from urllib.parse import urlencode
  
from collections import namedtuple

from bes.compat.url_compat import urljoin

class pcloud_requests(object):

  API = 'https://api.pcloud.com'

  _response = namedtuple('_response', 'url, status_code, payload')
  
  @classmethod
  def get(clazz, api_method, params):
    url = clazz._make_api_url(api_method)
    data = urlencode(params).encode('utf-8')
    req = Request(url, data = data)
    response = urlopen(req)
    content = response.read()
    status_code = response.getcode()
    if status_code == 200:
      payload = json.loads(content)
    else:
      payload = None
    return clazz._response(url, status_code, payload)
  
  @classmethod
  def _make_api_url(clazz, method):
    return urljoin(clazz.API, method)
