#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple

import base64

from ..system.check import check
from bes.system.compat import compat
from bes.compat import url_compat
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

from urllib import parse as urllib_parse

class url_util(object):
  'Url util'

  @classmethod
  def download_to_stream(clazz, url, stream, chunk_size = None, cookies = None, auth = None):
    'Download url to a stream in chunks.'
    try:
      import requests
      return clazz._download_to_stream_requests(url, stream, chunk_size = chunk_size, cookies = cookies, auth = auth)
    except ImportError as ex:
      return clazz._download_to_stream_python(url, stream, chunk_size = chunk_size, cookies = cookies, auth = auth)

  @classmethod
  def _download_to_stream_requests(clazz, url, stream, chunk_size = None, cookies = None, auth = None):
    'Download url to a stream in chunks.'
    check.check_dict(cookies, key_type = check.STRING_TYPES, value_type = check.STRING_TYPES, allow_none = True)

    import requests
    
    with requests.get(url, auth = auth, cookies = cookies, stream = True) as response:
      if response.status_code != 200:
        raise RuntimeError('Failed to download: {}'.format(url))
      for chunk in response.iter_content(chunk_size = 8192): 
        if chunk:
          stream.write(chunk)
      return response.status_code
  
  @classmethod
  def _download_to_stream_python(clazz, url, stream, chunk_size = None, cookies = None, auth = None):
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
  def download_to_temp_file(clazz, url, chunk_size = None, basename = None, delete = True, cookies = None, auth = None, suffix = None):
    'Download url to a temporary file.'
    if basename:
      assert file_util.is_basename(basename)
      tmp = path.join(temp_file.make_temp_dir(delete = delete), basename)
    else:  
      tmp = temp_file.make_temp_file(suffix = suffix)
    with open(tmp, 'wb') as fout:
      result = clazz.download_to_stream(url, fout, chunk_size = chunk_size, cookies = cookies, auth = auth)
      fout.close()
    return tmp
      
  _response = namedtuple('_response', 'status_code, content, headers')
  @classmethod
  def get(clazz, url, params = None):
    if params:
      data = url_compat.urlencode(params).encode('utf-8')
    else:
      data = None
    req = url_compat.Request(url, data = data)
    response = url_compat.urlopen(req)
    content = response.read()
    headers = response.headers.items()
    status_code = response.getcode()
    return clazz._response(status_code, content, headers)

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
      
    req = url_compat.Request(url, headers = headers)
    response = url_compat.urlopen(req)
    return response

  # this mess needs to be cleaned up with requests
  @classmethod
  def _get_py3(clazz, url, params = None, method = None):
    if params:
      data = url_compat.urlencode(params).encode('utf-8')
    else:
      data = None
    req = url_compat.Request(url, data = data, method = method)
    response = url_compat.urlopen(req)
    content = response.read()
    headers = response.headers.items()
    status_code = response.getcode()
    return clazz._response(status_code, content, headers)
  
  @classmethod
  def exists(clazz, url):
    'Return True if url exists by issuing a HEAD request for it.'
    try:
      response = clazz._get_py3(url, method = 'HEAD')
      return response.status_code == 200
    except Exception as ex:
      pass
    return False

  @classmethod
  def normalize(clazz, url):
    pu = urllib_parse.urlparse(url)
    if pu.path == '':
      new_path = '/'
    else:
      new_path = pu.path
    quoted_path = urllib_parse.quote(new_path)
    return urllib_parse.urlunparse(pu._replace(path = quoted_path))

  @classmethod
  def remove_query(clazz, url):
    pu = urllib_parse.urlparse(url)
    l = list(pu)
    l[4] = ''
    return urllib_parse.urlunparse(urllib_parse.ParseResult(*l))
  
