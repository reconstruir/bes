#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
from bes.system.compat import compat
from bes.compat import url_compat

from bes.testing.unit_test import unit_test
from bes.web.file_web_server import file_web_server
from bes.web.web_server_controller import web_server_controller
from bes.archive.archiver import archiver
from bes.fs.file_mime import file_mime
from bes.fs.file_util import file_util
from bes.url.url_util import url_util
from bes.fs.testing.temp_content import temp_content

class test_file_web_server(unit_test):

  def _make_temp_content(self, items):
    tmp_dir = self.make_temp_dir()
    temp_content.write_items(items, tmp_dir)
    return tmp_dir
  
  def test_download(self):
    
    tmp_dir = self._make_temp_content([
      'file foo.txt "this is foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "this is baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ])

    server = web_server_controller(file_web_server)
    server.start(root_dir = tmp_dir)
    port = server.address[1]

    url = self._make_url(port, 'foo.txt')
    download_tmp = url_util.download_to_temp_file(url)
    tmp = self.make_temp_file(suffix = '.txt')
    file_util.copy(download_tmp, tmp)
    self.assertEqual( 'text/plain', file_mime.mime_type(tmp).mime_type )
    self.assertEqual( 'this is foo.txt\n', file_util.read(tmp, codec = 'utf8') )

    url = self._make_url(port, 'subdir/subberdir/baz.txt')
    download_tmp = url_util.download_to_temp_file(url)
    tmp = self.make_temp_file(suffix = '.txt')
    file_util.copy(download_tmp, tmp)
    self.assertEqual( 'text/plain', file_mime.mime_type(tmp).mime_type )
    self.assertEqual( 'this is baz.txt\n', file_util.read(tmp, codec = 'utf8') )

    with self.assertRaises(url_compat.HTTPError) as ctx:
      url = self._make_url(port, 'notthere.txt')
      tmp = url_util.download_to_temp_file(url)

    server.stop()
    
  def test_download_with_auth(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "this is foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "this is baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ])

    server = web_server_controller(file_web_server)
    server.start(root_dir = tmp_dir, users = { 'fred': 'flintpass' })
    port = server.address[1]

    url = self._make_url(port, 'foo.txt')
    download_tmp = url_util.download_to_temp_file(url, auth = ('fred', 'flintpass'))
    tmp = self.make_temp_file(suffix = '.txt')
    file_util.copy(download_tmp, tmp)
    self.assertEqual( 'text/plain', file_mime.mime_type(tmp).mime_type )
    self.assertEqual( 'this is foo.txt\n', file_util.read(tmp, codec = 'utf8') )

    url = self._make_url(port, 'subdir/subberdir/baz.txt')
    download_tmp = url_util.download_to_temp_file(url, auth = ('fred', 'flintpass'))
    tmp = self.make_temp_file(suffix = '.txt')
    file_util.copy(download_tmp, tmp)
    self.assertEqual( 'text/plain', file_mime.mime_type(tmp).mime_type )
    self.assertEqual( 'this is baz.txt\n', file_util.read(tmp, codec = 'utf8') )

    with self.assertRaises(url_compat.HTTPError) as ctx:
      url = self._make_url(port, 'notthere.txt')
      tmp = url_util.download_to_temp_file(url)

    server.stop()

  @classmethod
  def _make_url(clazz, port, p):
    base = 'http://localhost:%d' % (port)
    return url_compat.urljoin(base, p)
  
if __name__ == '__main__':
  unit_test.main()
