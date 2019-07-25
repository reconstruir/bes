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

from bes.web.file_web_server_tester import file_web_server_tester

class test_file_web_server(unit_test):

  def test_download(self):
    items = [
      'file foo.txt "this is foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "this is baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]
    tester = file_web_server_tester(debug = self.DEBUG, items = items)
    tester.start()

    url = tester.make_url('foo.txt')
    download_tmp = url_util.download_to_temp_file(url, suffix = '.txt')
    self.assertEqual( 'text/plain', file_mime.mime_type(download_tmp).mime_type )
    self.assertEqual( 'this is foo.txt\n', file_util.read(download_tmp, codec = 'utf8') )

    url = tester.make_url('subdir/subberdir/baz.txt')
    download_tmp = url_util.download_to_temp_file(url, suffix = '.txt')
    self.assertEqual( 'text/plain', file_mime.mime_type(download_tmp).mime_type )
    self.assertEqual( 'this is baz.txt\n', file_util.read(download_tmp, codec = 'utf8') )

    with self.assertRaises(url_compat.HTTPError) as ctx:
      url = tester.make_url('notthere.txt')
      tmp = url_util.download_to_temp_file(url)

    tester.stop()
    
  def test_download_with_auth(self):
    items = [
      'file foo.txt "this is foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "this is baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]
    tester = file_web_server_tester(debug = self.DEBUG, items = items, users = { 'fred': 'flintpass' })
    tester.start()

    url = tester.make_url('foo.txt')
    download_tmp = url_util.download_to_temp_file(url, auth = ('fred', 'flintpass'), suffix = '.txt')
    self.assertEqual( 'text/plain', file_mime.mime_type(download_tmp).mime_type )
    self.assertEqual( 'this is foo.txt\n', file_util.read(download_tmp, codec = 'utf8') )

    url = tester.make_url('subdir/subberdir/baz.txt')
    download_tmp = url_util.download_to_temp_file(url, auth = ('fred', 'flintpass'), suffix = '.txt')
    self.assertEqual( 'text/plain', file_mime.mime_type(download_tmp).mime_type )
    self.assertEqual( 'this is baz.txt\n', file_util.read(download_tmp, codec = 'utf8') )

    with self.assertRaises(url_compat.HTTPError) as ctx:
      url = tester.make_url('notthere.txt')
      tmp = url_util.download_to_temp_file(url)

    tester.stop()

if __name__ == '__main__':
  unit_test.main()
