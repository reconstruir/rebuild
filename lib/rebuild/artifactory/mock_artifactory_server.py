#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os, os.path as path
from bes.web.web_server import web_server
from bes.system.log import log
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
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
        log.output('HEADER: %s=%s\n' % (key, value), console = True)

    if print_environ:
      for key, value in sorted(environ.items()):
        log.output('%s=%s\n' % (key, value), console = True)
    method = environ['REQUEST_METHOD']
    path_info = self.path_info(environ)
    if path_info.path_info.startswith('/api'):
      return self._api(environ, path_info, start_response)
    if method == 'GET':
      return self._get(environ, path_info, start_response)
    elif method == 'PUT':
      return self._put(environ, path_info, start_response)
    if method == 'HEAD':
      return self._head(environ, path_info, start_response)
    else:
      return self.response_error(start_response, 405)

  def _get(self, environ, path_info, start_response):
    if not path.isfile(path_info.rooted_filename):
      return self.response_error(start_response, 404)
    mime_type = self.mime_type(path_info.rooted_filename)
    content = file_util.read(path_info.rooted_filename)
    headers = [
      ( 'Content-Type', str(mime_type) ),
      ( 'Content-Length', str(len(content)) ),
      ( 'X-Artifactory-Filename', path.basename(path_info.path_info) ),
      ( 'X-Artifactory-Id', self._artifactory_id ),
    ]
    headers += artifactory_requests.checksum_headers_for_file(path_info.rooted_filename).items()
    return self.response_success(start_response, 200, [ content ], headers)

  def _head(self, environ, path_info, start_response):
    if not path.isfile(path_info.rooted_filename):
      return self.response_error(start_response, 404)
    mime_type = self.mime_type(path_info.rooted_filename)
    headers = [
      ( 'Content-Type', str(mime_type) ),
      ( 'Content-Length', str(file_util.size(path_info.rooted_filename)) ),
      ( 'X-Artifactory-Filename', path.basename(path_info.path_info) ),
      ( 'X-Artifactory-Id', self._artifactory_id ),
    ]
    headers += artifactory_requests.checksum_headers_for_file(path_info.rooted_filename).items()
    return self.response_success(start_response, 200, [], headers)
  
  def _put(self, environ, path_info, start_response):
    'https://www.jfrog.com/confluence/display/RTF/Artifactory+REST+API#ArtifactoryRESTAPI-DeployArtifact'
    content_length = int(environ['CONTENT_LENGTH'])
#    filename = environ['PATH_INFO']
#    filename = file_util.lstrip_sep(filename)
#    file_path = path.join(self._root_dir, filename)
    fin = environ['wsgi.input']
    chunk_size = 1024
    n = int(content_length / chunk_size)
    r = int(content_length % chunk_size)
    file_util.ensure_file_dir(path_info.rooted_filename)
    with open(path_info.rooted_filename, 'wb') as fout:
      for i in range(0, n):
        chunk = fin.read(chunk_size)
        fout.write(chunk)
      if r:
        chunk = fin.read(r)
        fout.write(chunk)
      fout.flush()
      fout.close()
    base = '%s://%s' % (environ['wsgi.url_scheme'], environ['HTTP_HOST'])
    uri = url_compat.urljoin(base, path_info.path_info)
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

  def _api(self, environ, path_info, start_response):
    parts = path_info.path_info.split('/')
    what = parts[2]
    if what == 'storage':
      return self._api_storage(environ, path_info, start_response)
    assert False

  def _api_storage(self, environ, path_info, start_response):
    xpath = file_util.remove_head(path_info.path_info, '/api/storage')
    fpath = path.join(self._root_dir, xpath)
    files = file_find.find(fpath, relative = True)
    for f in files:
      print('FILE: %s' % (f))
#    print(xpath)
    import sys
    sys.stdout.flush()
    assert False
