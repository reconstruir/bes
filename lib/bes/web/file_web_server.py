#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
from .web_server import web_server

from bes.fs.file_util import file_util
from bes.files.bf_path import bf_path
from bes.fs.testing.temp_content import temp_content
from bes.archive.temp_archive import temp_archive

class file_web_server(web_server):
  'A simple web server that serves whatever files are found in its root dir'

  def __init__(self, root_dir, *args, **kargs):
    super(file_web_server, self).__init__(log_tag = 'file_web_server', *args, **kargs)
    self._root_dir = root_dir
      
  def handle_request(self, environ, start_response):
    path_info = self.path_info(environ)
    if not path.isfile(path_info.rooted_filename):
      return self.response_error(start_response, 404)
    mime_type = self.mime_type(path_info.rooted_filename)
    content = file_util.read(path_info.rooted_filename)
    headers = [
      ( 'Content-Type', str(mime_type) ),
      ( 'Content-Length', str(len(content)) ),
    ]
    return self.response_success(start_response, 200, [ content ], headers)

  def write_temp_content(self, items):
    temp_content.write_items(items, self._root_dir)

  def write_file(self, filename, content, codec = 'utf-8', mode = None):
    p = self.file_path(filename)
    if path.exists(p):
      raise IOError('already existsL {}'.format(filename))
    file_util.save(p, content = content, codec = codec, mode = mode)

  def read_file(self, filename, codec = 'utf-8'):
    return file_util.read(self.file_path(filename), codec = codec)

  def has_file(self, filename):
    return path.exists(self.file_path(filename))

  def file_path(self, filename):
    return path.join(self._root_dir, filename)

  def write_archive(self, filename, items):
    p = self.file_path(filename)
    if path.exists(p):
      raise IOError('already existsL {}'.format(filename))
    extension = file_util.extension(filename)
    tmp_archive = temp_archive.make_temp_archive(items, extension)
    file_util.rename(tmp_archive, p)
