#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.system.check import check

from .bopenssl_command import bopenssl_command
from .bopenssl_error import bopenssl_error

class bopenssl_digest(object):

  @classmethod
  def sha256(clazz, filepath):
    'Return the hex sha256 digest of filepath.'
    check.check_string(filepath)
    if not path.exists(filepath):
      raise bopenssl_error(f'file not found: {filepath}')
    rv = bopenssl_command.call_command(['dgst', '-sha256', filepath])
    # output is "SHA256(path)= <hex>" or "SHA2-256(path)= <hex>"
    line = rv.stdout.strip()
    if '= ' not in line:
      raise bopenssl_error(f'unexpected openssl output: {line}')
    return line.split('= ', 1)[1].lower()

  @classmethod
  def sha512_crypt(clazz, password):
    'Return a $6$... SHA-512 crypt hash suitable for HAProxy userlist or htpasswd.'
    check.check_string(password)
    rv = bopenssl_command.call_command(
      ['passwd', '-6', '-stdin'],
      input_data=(password + '\n').encode('utf-8'),
    )
    result = rv.stdout.strip()
    if not result.startswith('$6$'):
      raise bopenssl_error(f'unexpected openssl passwd output (is this LibreSSL?): {result}')
    return result
