#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.compat.url_compat import urljoin, urlopen, urlencode, Request
from bes.fs import file_util, temp_file

class url_util(object):
  'Url util'

  @classmethod
  def download_to_stream(clazz, url, stream, chunk_size = None):
    'Download url to a stream in chunks.'
    response = urlopen(url)
    status_code = response.getcode()
    if status_code != 200:
      return status_code
    chunk_size = chunk_size or 1024
    while True:
      chunk = response.read(chunk_size)
      if not chunk:
        break
      stream.write(chunk)
    return status_code

  @classmethod
  def download_to_file(clazz, url, filename, chunk_size = None):
    'Download url to filename.'
    tmp = temp_file.make_temp_file(suffix = '.download')
    with open(tmp, 'wb') as fout:
      result = clazz.download_to_stream(url, fout, chunk_size = chunk_size)
      fout.close()
      file_util.copy(tmp, filename)
      file_util.remove(tmp)

  _response = namedtuple('_response', 'status_code, content')
  @classmethod
  def get(clazz, url, params = None):
    if params:
      data = urlencode(params).encode('utf-8')
    else:
      data = None
    req = Request(url, data = data)
    response = urlopen(req)
    content = response.read()
    status_code = response.getcode()
    return clazz._response(status_code, content)
