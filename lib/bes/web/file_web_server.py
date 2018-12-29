#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
from .web_server import web_server

from bes.fs import file_mime, file_util

class file_web_server(web_server):
  'A simple web server that serves whatever files are found in its root dir'

  def __init__(self, port = None, root_dir = None):
    super(file_web_server, self).__init__(port = port, log_tag = 'file_web_server')
    self._root_dir = root_dir or os.getcwd()

  _ERROR_404_HTML = '''
<html>
  <head>
    <title>404 - Not Found</title>
  </head>
  <body>
    <h1>404 - Not Found</h1>
  </body>
</html>
'''
      
  def handle_request(self, environ, start_response):
    filename = environ['PATH_INFO']
    self.log_i('handle_request: filename=%s' % (filename))
    file_path = path.join(self._root_dir, file_util.lstrip_sep(filename))
    self.log_d('handle_request: file_path=%s' % (file_path))
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
