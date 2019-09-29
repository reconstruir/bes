#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.compat import compat

if compat.IS_PYTHON3:
  import urllib.parse as urlparse
else:
  import urlparse as urlparse
  
from bes.testing.unit_test import unit_test
from bes.web.file_web_server import file_web_server
from bes.web.web_server_controller import web_server_controller
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.url.http_download_cache import http_download_cache
from bes.fs.testing.temp_content import temp_content

class test_http_download_cache(unit_test):

  @classmethod
  def _make_temp_content(clazz, items):
    tmp_dir = temp_file.make_temp_dir()
    temp_content.write_items(items, tmp_dir)
    return tmp_dir
  
  def test_tarball_server(self):
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

    cache = http_download_cache(temp_file.make_temp_dir())

    url = self._make_url(port, 'foo.txt')

    self.assertFalse( cache.has_url(url) )
    self.assertEqual( "this is foo.txt\n", file_util.read(cache.get_url(url), codec = 'utf-8') )
    self.assertTrue( cache.has_url(url) )

    
    
    server.stop()

  @classmethod
  def _make_url(clazz, port, p):
    base = 'http://localhost:%d' % (port)
    return urlparse.urljoin(base, p)
  
if __name__ == '__main__':
  unit_test.main()
