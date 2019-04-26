#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
from .web_server import web_server

from bes.fs import file_mime, file_util

class file_web_server(web_server):
  'A simple web server that serves whatever files are found in its root dir'

  def __init__(self, root_dir, *args, **kargs):
    super(file_web_server, self).__init__(log_tag = 'file_web_server', *args, **kargs)
    self._root_dir = root_dir
      
  def handle_request(self, environ, start_response):
    filename = environ['PATH_INFO']
    self.log_i('handle_request: filename=%s' % (filename))
    file_path = path.join(self._root_dir, file_util.lstrip_sep(filename))
    self.log_d('handle_request: file_path=%s' % (file_path))
    if not path.isfile(file_path):
      return self.response_error(start_response, 404)
    mime_type = file_mime.mime_type(file_path)
    content = file_util.read(file_path)
    headers = [
      ( 'Content-Type', str(mime_type) ),
      ( 'Content-Length', str(len(content)) ),
    ]
    return self.response_success(start_response, 200, [ content ], headers)
