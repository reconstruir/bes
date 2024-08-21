#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path

from bes.archive.temp_archive import temp_archive
from bes.compat import url_compat
from bes.fs.file_util import file_util
from bes.fs.file_find import file_find
from bes.fs.temp_file import temp_file
from bes.fs.testing.temp_content import temp_content

from ..files.find.bf_file_finder import bf_file_finder
from ..files.find.bf_file_finder_options import bf_file_finder_options
from ..files.bf_file_type import bf_file_type

from .file_web_server import file_web_server
from .web_server_controller import web_server_controller

class file_web_server_tester(object):
  'A class to test a file_web_server'

  def __init__(self, root_dir = None, debug = False, items = None, users = None):
    self.root_dir = root_dir or temp_file.make_temp_dir(delete = not debug)
    if items:
      self.write_temp_content(items)
    self.server = None
    self.port = None
    self.users = users

  def start(self):
    assert not self.server
    self.server = web_server_controller(file_web_server)
    self.server.start(root_dir = self.root_dir, users = self.users)
    self.port = self.server.address[1]

  def stop(self):
    assert self.server
    self.server.stop()
    
  def make_url(self, p = None):
    assert self.port
    base = 'http://localhost:{}'.format(self.port)
    if not p:
      return base
    return url_compat.urljoin(base, p)
    
  def write_temp_content(self, items):
    temp_content.write_items(items, self.root_dir)
    
  def write_file(self, filename, content, codec = 'utf-8', mode = None):
    p = self.file_path(filename)
    if path.exists(p):
      raise IOError('already existsL {}'.format(filename))
    file_util.save(p, content = content, codec = codec, mode = mode)

  def read_file(self, filename, codec = 'utf-8'):
    return file_util.read(self.file_path(filename), codec = codec)

  def file_checksum(self, filename):
    return file_util.checksum('sha256', self.file_path(filename))

  def has_file(self, filename):
    return path.exists(self.file_path(filename))

  def file_path(self, filename):
    return path.join(self.root_dir, filename)

  def write_archive(self, filename, items):
    p = self.file_path(filename)
    if path.exists(p):
      raise IOError('already exists {}'.format(filename))
    extension = file_util.extension(filename)
    tmp_archive = temp_archive.make_temp_archive(items, extension)
    file_util.rename(tmp_archive, p)

  def find_all_files(self, relative = True):
    assert False
    options = bf_file_finder_options(relative = relative,
                              file_type = bf_file_type.FILE_OR_LINK)
    f = bf_file_finder(options = options)
    r1 = f.find(self.root_dir)
    r2 = file_find.find(self.root_dir, relative = relative, file_type = file_find.FILE | file_find.LINK)
    print(f'r1={r1}', flush = True)
    print(f'r2={r2}', flush = True)
    return r2
