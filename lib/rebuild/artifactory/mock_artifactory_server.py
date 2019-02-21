#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os, os.path as path
from bes.web import web_server
from bes.fs import file_mime, file_util
from bes.compat import url_compat

class mock_artifactory_server(web_server):
  'A mock artifactory web server.  Tries to impersonate artifactory enough to do unit tests.'

  def __init__(self, port = None, root_dir = None):
    super(mock_artifactory_server, self).__init__(port = port, log_tag = 'file_web_server')
    self._root_dir = root_dir or os.getcwd()

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
    if True:
      for key, value in sorted(self.headers.items()):
        print('HEADER: %s=%s' % (key, value))
    
    print_environ = False
    #print_environ = True
    if print_environ:
      for key, value in sorted(environ.items()):
        print('%s=%s' % (key, value))
    method = environ['REQUEST_METHOD']
    if method == 'GET':
      return self._get(environ, start_response)
    elif method == 'PUT':
      return self._put(environ, start_response)
    else:
      start_response('405 Not supported', [
        ( 'Content-Type', 'text/html' ),
        ( 'Content-Length', str(len(self._ERROR_405_HTML)) ),
      ])
      return iter([ self._ERROR_405_HTML ])

  def _get(self, environ, start_response):
    filename = environ['PATH_INFO']
    file_path = path.join(self._root_dir, file_util.lstrip_sep(filename))
    if not path.isfile(file_path):
      start_response('404 Not Found', [
        ( 'Content-Type', 'text/html' ),
        ( 'Content-Length', str(len(self._ERROR_404_HTML)) ),
      ])
      return iter([ self._ERROR_404_HTML ])
    mime_type = file_mime.mime_type(file_path)
    content = file_util.read(file_path)
    start_response('200 OK', [
      ( 'Content-Type', str(mime_type) ),
      ( 'Content-Length', str(len(content)) ),
    ])
    return iter([ content ])
 
  def _put(self, environ, start_response):
    'https://www.jfrog.com/confluence/display/RTF/Artifactory+REST+API#ArtifactoryRESTAPI-DeployArtifact'
    content_length = int(environ['CONTENT_LENGTH'])
    filename = environ['PATH_INFO']
    filename = file_util.lstrip_sep(filename)
    file_path = path.join(self._root_dir, filename)
    fin = environ['wsgi.input']
    chunk_size = 1024
    n = content_length / chunk_size
    r = content_length % chunk_size
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
    start_response('201 Created', [
      ( 'Content-Type', 'application/json' ),
      ( 'Content-Length', str(len(content)) ),
    ])
    return iter([ content ])
