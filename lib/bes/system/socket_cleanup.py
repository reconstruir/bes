#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import atexit
import socket

from .check import check

class socket_cleanup(object):

  def __init__(self, cleanup = True):
    check.check_bool(cleanup)
    
    self._cleanup = cleanup
    self._original_socket_func = None
    
  def __enter__(self):
    self._original_socket_func = socket.socket

    def _new_socket_func(*args, **kargs):
      s = self._original_socket_func(*args, **kargs)
      if self._cleanup:
        def _cleanup():
          s.close()
        atexit.register(_cleanup)
      return s
    socket.socket = _new_socket_func
    
  def __exit__(self, type, value, traceback):
    socket.socket = self._original_socket_func
