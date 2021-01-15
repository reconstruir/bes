#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import socket
import errno

from bes.common.check import check
from bes.system.log import logger

class port_probe(object):

  _log = logger('port_probe')
  
  @classmethod
  def is_open(clazz, address):
    check.check_tuple(address)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      rv = sock.connect_ex(address)
    except Exception as ex:
      clazz._log.log_d('caught: {}'.format(str(ex)))
      return False
      
    if rv != 0:
      clazz._log.log_d('not open: {} - {} - {}'.format(address, rv, errno.errorcode[rv]))
    return rv == 0
