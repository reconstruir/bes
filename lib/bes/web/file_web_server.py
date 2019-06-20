#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
from .web_server import web_server

from bes.fs.file_mime import file_mime
from bes.fs.file_util import file_util
from bes.fs.file_path import file_path

class file_web_server(web_server):
  'A simple web server that serves whatever files are found in its root dir'

  def __init__(self, root_dir, *args, **kargs):
    super(file_web_server, self).__init__(log_tag = 'file_web_server', *args, **kargs)
    self._root_dir = root_dir
      
  def handle_request(self, environ, start_response):
    filename = file_path.normalize_sep(environ['PATH_INFO'])
    fragment = file_util.lstrip_sep(filename)
    self.log_d('handle_request: filename={} fragment={} root_dir={}'.format(filename, fragment, self._root_dir))
    filename_abs = path.join(self._root_dir, fragment)
    self.log_i('handle_request: filename_abs={}'.format(filename_abs))
    if not path.isfile(filename_abs):
      return self.response_error(start_response, 404)
    mime_type = file_mime.mime_type(filename_abs)
    content = file_util.read(filename_abs)
    headers = [
      ( 'Content-Type', str(mime_type) ),
      ( 'Content-Length', str(len(content)) ),
    ]
    return self.response_success(start_response, 200, [ content ], headers)
