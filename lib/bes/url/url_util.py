#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple

import base64

from bes.common.check import check
from bes.system.compat import compat
from bes.compat.url_compat import urljoin, urlopen, urlencode, urlparse, Request
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.key_value.key_value import key_value

class url_util(object):
  'Url util'

  @classmethod
  def download_to_stream(clazz, url, stream, chunk_size = None, cookies = None, auth = None):
    'Download url to a stream in chunks.'
    check.check_dict(cookies, key_type = check.STRING_TYPES, value_type = check.STRING_TYPES, allow_none = True)
    response = clazz._url_open(url, cookies = cookies, auth = auth)
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
  def download_to_file(clazz, url, filename, chunk_size = None, cookies = None, auth = None):
    'Download url to filename.'
    tmp = clazz.download_to_temp_file(url, chunk_size = chunk_size, cookies = cookies, auth = auth)
    file_util.copy(tmp, filename)
    file_util.remove(tmp)

  @classmethod
  def download_to_temp_file(clazz, url, chunk_size = None, basename = None, delete = True, cookies = None, auth = None):
    'Download url to a temporary file.'
    if basename:
      assert file_util.is_basename(basename)
      tmp = path.join(temp_file.make_temp_dir(delete = delete), basename)
    else:  
      tmp = temp_file.make_temp_file(suffix = '.download')
    with open(tmp, 'wb') as fout:
      result = clazz.download_to_stream(url, fout, chunk_size = chunk_size, cookies = cookies, auth = auth)
      fout.close()
    return tmp
      
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

  @classmethod
  def url_path_baename(clazz, url):
    return path.basename(urlparse(url).path)
  
  @classmethod
  def _url_open(clazz, url, cookies = None, auth = None):
    'Python 2 and 3 url open compatibility wrapper.'
    if compat.IS_PYTHON2:
      return clazz._url_open_2(url, cookies = cookies, auth = auth)
    elif compat.IS_PYTHON3:
      return clazz._url_open_3(url, cookies = cookies, auth = auth)
    else:
      raise RuntimeError('Unknown python version')
  
  @classmethod
  def _url_open_2(clazz, url, cookies = None, auth = None):
    'Python 2 url open.'
    import urllib2

    opener = urllib2.build_opener()

    if auth:
      base64string = base64.encodestring('%s:%s' % (auth[0], auth[1])).replace('\n', '')
      opener.addheaders.append(('Authorization', 'Basic {}'.format(base64string)))
    
    if cookies:
      flat_cookies = '; '.join('%s=%s' % (key, value) for key, value in cookies.items())
      opener.addheaders.append(('Cookie', flat_cookies))
      
    response = opener.open(url)
    return response

  @classmethod
  def _url_open_3(clazz, url, cookies = None, auth = None):
    'Python 3 url open.'
    headers = {}

    if auth:
      colon_auth = '{}:{}'.format(*auth).encode('utf8')
      auth_header = base64.encodebytes(colon_auth).replace(b'\n', b'')
      auth_header = auth_header.decode('utf8')
      headers['Authorization'] = 'Basic {}'.format(auth_header)
    
    if cookies:
      headers = headers or {}
      flat_cookies = '; '.join('%s=%s' % (key, value) for key, value in cookies.items())
      headers['Cookie'] = flat_cookies
      
    req = Request(url, headers = headers)
    response = urlopen(req)
    return response
