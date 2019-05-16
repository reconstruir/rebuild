#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os, os.path as path
from bes.web import web_server
from bes.system import log
from bes.fs import file_mime, file_find, file_util
from bes.compat import url_compat

from .artifactory_requests import artifactory_requests

class mock_artifactory_server(web_server):
  'A mock artifactory web server.  Tries to impersonate artifactory enough to do unit tests.'

  def __init__(self, port = None, root_dir = None, artifactory_id = '', users = None):
    super(mock_artifactory_server, self).__init__(port = port, users = users, log_tag = 'file_web_server')
    self._root_dir = root_dir or os.getcwd()
    self._artifactory_id = artifactory_id

  _ERROR_404_HTML = '''
<html>
  <head>
    <title>404 - Not found</title>
  </head>
  <body>
    <h1>404 - Not found</h1>
  </body>
</html>
'''

  _ERROR_405_HTML = '''
<html>
  <head>
    <title>405 - Method not supported</title>
  </head>
  <body>
    <h1>405 - Method not supported</h1>
  </body>
</html>
'''
  
  def handle_request(self, environ, start_response):
    print_environ = False
    #print_environ = True
    
    print_headers = False
    #print_headers = True

    if print_headers:
      for key, value in sorted(self.headers.items()):
        log._console_output('HEADER: %s=%s\n' % (key, value))

    if print_environ:
      for key, value in sorted(environ.items()):
        log._console_output('%s=%s\n' % (key, value))
    method = environ['REQUEST_METHOD']
    filename = environ['PATH_INFO']
    if filename.startswith('/api'):
      return self._api(environ, start_response)
    if method == 'GET':
      return self._get(environ, start_response)
    elif method == 'PUT':
      return self._put(environ, start_response)
    if method == 'HEAD':
      return self._head(environ, start_response)
    else:
      return self.response_error(start_response, 405)

  def _get(self, environ, start_response):
    filename = environ['PATH_INFO']
    file_path = path.join(self._root_dir, file_util.lstrip_sep(filename))
    if not path.isfile(file_path):
      return self.response_error(start_response, 404)
    mime_type = file_mime.mime_type(file_path)
    content = file_util.read(file_path)
    headers = [
      ( 'Content-Type', str(mime_type) ),
      ( 'Content-Length', str(len(content)) ),
      ( 'X-Artifactory-Filename', path.basename(file_path) ),
      ( 'X-Artifactory-Id', self._artifactory_id ),
    ]
    headers += artifactory_requests.checksum_headers_for_file(file_path).items()
    return self.response_success(start_response, 200, [ content ], headers)

  def _head(self, environ, start_response):
    filename = environ['PATH_INFO']
    file_path = path.join(self._root_dir, file_util.lstrip_sep(filename))
    if not path.isfile(file_path):
      return self.response_error(start_response, 404)
    mime_type = file_mime.mime_type(file_path)
    headers = [
      ( 'Content-Type', str(mime_type) ),
      ( 'Content-Length', str(file_util.size(file_path)) ),
      ( 'X-Artifactory-Filename', path.basename(file_path) ),
      ( 'X-Artifactory-Id', self._artifactory_id ),
    ]
    headers += artifactory_requests.checksum_headers_for_file(file_path).items()
    return self.response_success(start_response, 200, [], headers)
  
  def _put(self, environ, start_response):
    'https://www.jfrog.com/confluence/display/RTF/Artifactory+REST+API#ArtifactoryRESTAPI-DeployArtifact'
    content_length = int(environ['CONTENT_LENGTH'])
    filename = environ['PATH_INFO']
    filename = file_util.lstrip_sep(filename)
    file_path = path.join(self._root_dir, filename)
    fin = environ['wsgi.input']
    chunk_size = 1024
    n = int(content_length / chunk_size)
    r = int(content_length % chunk_size)
    file_util.ensure_file_dir(file_path)
    with open(file_path, 'wb') as fout:
      for i in range(0, n):
        chunk = fin.read(chunk_size)
        fout.write(chunk)
      if r:
        chunk = fin.read(r)
        fout.write(chunk)
      fout.flush()
      fout.close()
    base = '%s://%s' % (environ['wsgi.url_scheme'], environ['HTTP_HOST'])
    uri = url_compat.urljoin(base, filename)
    data = {
      'downloadUri': uri,
    }
    content = json.dumps(data, indent = 2) + '\n'
    content = content.encode('utf8')
    headers = [
      ( 'Content-Type', 'application/json' ),
      ( 'Content-Length', str(len(content)) ),
    ]
    return self.response_success(start_response, 201, [ content ], headers)

  def _api(self, environ, start_response):
    filename = environ['PATH_INFO']
    parts = filename.split('/')
    what = parts[2]
    if what == 'storage':
      return self._api_storage(environ, start_response)
    assert False

  def _api_storage(self, environ, start_response):
    filename = environ['PATH_INFO']
    xpath = file_util.remove_head(filename, '/api/storage')
    fpath = path.join(self._root_dir, xpath)
    files = file_find.find(fpath, relative = True)
    for f in files:
      print('FILE: %s' % (f))
#    print(xpath)
    import sys
    sys.stdout.flush()
    assert False
    
