#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
from bes.system.compat import compat
from bes.system.host import host
from bes.compat import url_compat
  
from bes.testing.unit_test import unit_test
from bes.web.web_server import web_server
from bes.web.web_server_controller import web_server_controller
from bes.archive.archiver import archiver
from bes.archive.temp_archive import temp_archive
from bes.fs.file_mime import file_mime
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.url.url_util import url_util
from bes.testing.unit_test_function_skip import unit_test_function_skip
from bes.system.host import host
from bes.system.bdocker import bdocker

class test_web_server(unit_test):

  @classmethod
  def setUpClass(clazz):
    bdocker.raise_skip_if_running_under_docker()
  
  class _json_web_server(web_server):

    def __init__(self, port = None):
      web_server.__init__(self, port = port, log_tag = '_json_web_server')
      self._count = 0
      
    def handle_request(self, environ, start_response):
      self._count += 1
      path_info = environ['PATH_INFO']
      self.log_i('handle_request(%s)' % (path_info))
      response = {
        'payload': 'nice server: %s\n' % (path_info),
        'count': self._count,
      }
      content = json.dumps(response, indent = 2).encode('utf8')
      start_response('200 OK', [
        ( 'Content-Type', 'text/html; charset=utf-8' ),
        ( 'Content-Length', str(len(content)) ),
      ])
      return iter([ content ])

  def xtest_json(self):
    server = web_server_controller(self._json_web_server)
    server.start()
    port = server.address[1]

    url = self._make_url(port, 'foo')
    content = url_compat.urlopen(url).read()
    response = json.loads(content)
    self.assertEqual( { 'payload': 'nice server: /foo\n', 'count': 1 }, response )

    url2 = self._make_url(port, 'bar/baz')
    content = url_compat.urlopen(url2).read()
    response = json.loads(content)
    self.assertEqual( { 'payload': 'nice server: /bar/baz\n', 'count': 2 }, response )
    
    server.stop()
    
  @classmethod
  def _make_url(clazz, port, p):
    base = 'http://localhost:%d' % (port)
    return url_compat.urljoin(base, p)

  class _tarball_web_server(web_server):

    def __init__(self, port = None):
      web_server.__init__(self, port = port, log_tag = '_tarball_web_server')
      self._known_tarballs = {
        '/sources/foo/foo-1.2.3.tar.gz',
        '/sources/bar/bar-1.2.3.zip',
        '/sources/large/large-1.2.3.tar.gz',
      }
      
    def handle_request(self, environ, start_response):
      path_info = environ['PATH_INFO']
      self.log_i('handle_request(%s)' % (path_info))
      if path_info not in self._known_tarballs:
        return self.response_error(start_response, 404)
      extension = file_util.extension(path_info)
      if 'large' in path_info:
        items = [
          temp_archive.item('kiwi.bin', content = self._make_large_content()),
        ]
      else:
        items = [
          temp_archive.item('apple.txt', content = 'apple.txt\n'),
          temp_archive.item('orange.txt', content = 'orange.txt\n'),
        ]
      tmp_archive = temp_archive.make_temp_archive(items, extension)
      tmp_mime_type = file_mime.mime_type(tmp_archive)
      content = file_util.read(tmp_archive)
      headers = [
        ( 'Content-Type', str(tmp_mime_type) ),
        ( 'Content-Length', str(len(content)) ),
      ]
      result = self.response_success(start_response, 200, [ content ], headers)
      file_util.remove(tmp_archive)
      return result

    _LARGE_CONTENT_SIZE = 1024 * 1024 * 10 # 10M
    @classmethod
    def _make_large_content(clazz):
      return b'x' * clazz._LARGE_CONTENT_SIZE

  def xtest_tarball(self):
    server = web_server_controller(self._tarball_web_server)
    server.start()
    port = server.address[1]

    url = self._make_url(port, 'sources/foo/foo-1.2.3.tar.gz')
    tmp = url_util.download_to_temp_file(url, basename = 'foo-1.2.3.tar.gz')
    self.debug_spew_filename('tmp', tmp)
    self.assertEqual( [ 'apple.txt', 'orange.txt' ], archiver.members(tmp) )
    self.assertTrue( file_mime.is_gzip(tmp) )
    file_util.remove(tmp)
    
    url = self._make_url(port, 'sources/bar/bar-1.2.3.zip')
    tmp = url_util.download_to_temp_file(url, basename = 'bar-1.2.3.zip')
    self.debug_spew_filename('tmp', tmp)
    self.assertEqual( [ 'apple.txt', 'orange.txt' ], archiver.members(tmp) )
    self.assertTrue( file_mime.is_zip(tmp) )
    file_util.remove(tmp)
    
    server.stop()
    
  def xtest_fail_next_request(self):
    server = web_server_controller(self._tarball_web_server)
    server.start()
    port = server.address[1]

    url = self._make_url(port, 'sources/foo/foo-1.2.3.tar.gz')
    tmp = url_util.download_to_temp_file(url, basename = 'foo-1.2.3.tar.gz')
    self.assertEqual( [ 'apple.txt', 'orange.txt' ], archiver.members(tmp) )
    file_util.remove(tmp)

    server.fail_next_request(404)

    with self.assertRaises( ( url_compat.HTTPError, RuntimeError ) ) as ctx:
      url_util.download_to_temp_file(url, basename = 'foo-1.2.3.tar.gz')

    tmp = url_util.download_to_temp_file(url, basename = 'foo-1.2.3.tar.gz')
    self.assertEqual( [ 'apple.txt', 'orange.txt' ], archiver.members(tmp) )
    file_util.remove(tmp)
      
    server.stop()
    
  @unit_test_function_skip.skip_if(host.DISTRO == 'fedora', 'FIXME: this test fails on fedora')
  def test_tarball_large(self):
    server = web_server_controller(self._tarball_web_server)
    server.start()
    port = server.address[1]

    url = self._make_url(port, 'sources/large/large-1.2.3.tar.gz')
    tmp = url_util.download_to_temp_file(url, basename = 'large-1.2.3.tar.gz')
    self.debug_spew_filename('tmp', tmp)
    self.assertEqual( [ 'kiwi.bin' ], archiver.members(tmp) )
    self.assertTrue( file_mime.is_gzip(tmp) )
    file_util.remove(tmp)

    server.stop()
    
if __name__ == '__main__':
  unit_test.main()
