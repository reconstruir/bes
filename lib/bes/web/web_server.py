#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import base64, multiprocessing
from wsgiref import simple_server
from collections import namedtuple

from abc import abstractmethod, ABCMeta

from ..system.check import check
from bes.fs.file_mime import file_mime
from bes.fs.file_path import file_path
from bes.fs.file_util import file_util
from bes.system.log import log

class web_server(object, metaclass = ABCMeta):

  class handler(simple_server.WSGIRequestHandler):

    def __init__(self, request, client_address, server):
      log.add_logging(self, 'web_server')
      simple_server.WSGIRequestHandler.__init__(self, request, client_address, server)
      
    def log_message(self, format, *args):
      m = "%s - - [%s] %s\n" % (self.client_address[0],
                                self.log_date_time_string(),
                                format % args)
      self.log_i(m)
      
  def __init__(self, port = None, log_tag = None, users = None):
    log.add_logging(self, tag = log_tag or 'web_server')
    self.log_i('web_server(id={} self={}, port={})'.format(id(self), self, port))
    self._users = users or {}
    self._requested_port = port
    self.address = None
    self._process = None
    self._port_queue = multiprocessing.Queue()
    self._fail_next_request = multiprocessing.Value('i', 0)
    
  @abstractmethod
  def handle_request(self, environ, start_response):
    pass

  class _status_code(namedtuple('_status_code', 'code, status_message')):
    def __new__(clazz, code, status_message):
      check.check_int(code)
      check.check_string(status_message)
      return clazz.__bases__[0].__new__(clazz, code, status_message)
    _HTML_STATUS_TEMPLATE = '''
<html>
  <head>
    <title>{status_message}</title>
  </head>
  <body>
    <h1>{status_message}</h1>
  </body>
</html>
'''
    @property
    def html(self):
      return self._HTML_STATUS_TEMPLATE.format(status_message = self.status_message)

    @property
    def headers(self):
      return [
        ( 'Content-Type', 'text/html' ),
        ( 'Content-Length', str(len(self.html)) ),
      ]
    
  _RESPONSE_CODES = {
    200: _status_code(200, '200 OK'),
    201: _status_code(200, '201 Created'),
    403: _status_code(403, '403 Wrong username or password'),
    404: _status_code(403, '404 Not found'),
    405: _status_code(405, '405 Method not supported'),
  }
  
  def _server_process(self):

    def _handler(environ, start_response):
      self.log_d('_handler: id={} self={} _fail_next_request={}'.format(id(self), self, self._fail_next_request))
      self.headers = self._get_headers(environ)
      self.log_d('headers={}'.format(self.headers))
      auth = self._decode_auth(environ)
      if not self._validate_auth(auth):
        return self.response_error(start_response, 403)
      if self._fail_next_request.value != 0:
        code = self._fail_next_request.value
        self._fail_next_request.value = 0
        return self.response_error(start_response, code)
      result = self.handle_request(environ, start_response)
      return result
    log.add_logging(self, 'web_server')
    httpd = simple_server.make_server('', self._requested_port or 0, _handler, handler_class = self.handler)
    httpd.allow_reuse_address = True
    address = httpd.socket.getsockname()
    self.log_i('notifying that port is known')
    self._port_queue.put(address)
    self.log_i('calling serve_forever()')
    httpd.serve_forever()

  _auth = namedtuple('_auth', 'username, password')
  @classmethod
  def _decode_auth(clazz, environ):
    auth = environ.get('HTTP_AUTHORIZATION', None)
    clazz.log_i('_decode_auth: HTTP_AUTHORIZATION={}'.format(auth))
    if not auth:
      return None
    scheme, data = auth.split(None, 1)
    assert scheme.lower() == 'basic'
    decoded_data = base64.b64decode(data).decode('utf-8')
    username, password = decoded_data.split(':', 1)
    return clazz._auth(username, password)

  def _validate_auth(self, auth):
    self.log_i('_validate_auth: users={} auth={}'.format(self._users, auth))
    if not self._users:
      self.log_d('_validate_auth_auth: no users given.')
      return True
    if not auth:
      self.log_d('_validate_auth_auth: no auth given.')
      return False
    password = self._users.get(auth.username, None)
    if password is None:
      self.log_d('_validate_auth_auth: no password found for {}'.format(auth.username))
      return False
    if password != auth.password:
      self.log_d('_validate_auth_auth: password for {} is wrong'.format(auth.username))
      return False
    return True
  
  def response_error(self, start_response, code):
    self.log_d('response_error: code='.format(code))
    rc = self._RESPONSE_CODES[code]
    start_response(rc.status_message, rc.headers)
    return iter([ rc.html.encode('utf-8') ])
    
  def response_success(self, start_response, code, content, headers):
    check.check_list(content)
#    for c in content:
#      if not hasattr(c, 'decode'):
#        raise RuntimeError('content should be bytes instead of: {} - "{}"'.format(type(c), str(c)))
#      d = c.encode('utf-8')
    rc = self._RESPONSE_CODES[code]
    start_response(rc.status_message, headers)
    return iter(content)
    
  def start(self):
    self._process = multiprocessing.Process(name = 'web_server', target = self._server_process)
    self._process.daemon = True
    self._process.start()
    self.log_i('waiting for port known notification')
    self.address = self._port_queue.get()
  
  def stop(self):
    self._process.terminate()
    self._process.join()

  @classmethod
  def _get_headers(clazz, environ):
    headers = {}
    for key, value in sorted(environ.items()):
      if key.startswith('HTTP_'):
        headers[key[5:].lower()] = value
    return headers
    
  def fail_next_request(self, status_code):
    'Fail the next request with the given status_code.'
    self.log_d('fail_next_request: id={} self={} status_code={}'.format(id(self), self, status_code))
    self._fail_next_request.value = status_code

  _path_info = namedtuple('_path_info', 'path_info, filename, fragment, rooted_filename')
  def path_info(self, environ, relative = True):
    path_info = environ['PATH_INFO']
    filename = file_path.normalize_sep(path_info)
    fragment = file_util.lstrip_sep(filename)
    rooted_filename = path.join(self._root_dir, fragment)
    return self._path_info(path_info, filename, fragment, rooted_filename)

  def mime_type(self, filename):
    return file_mime.mime_type(filename)
