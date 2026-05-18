#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path
import stat

from bes.system.check import check

from .bssh_error import bssh_error
from .bssh_keygen_command import bssh_keygen_command

class bssh_keygen(object):

  @classmethod
  def generate_ed25519(clazz, key_path, comment=''):
    'Generate a passwordless ed25519 key pair at key_path and key_path.pub.'
    check.check_string(key_path)
    check.check_string(comment)
    key_path = path.abspath(key_path)
    if path.exists(key_path):
      raise bssh_error(f'key path already exists: {key_path}')
    cmd = ['-t', 'ed25519', '-N', '', '-C', comment, '-f', key_path]
    bssh_keygen_command.call_command(cmd, quote=False)
    # ssh-keygen should set 0600 but enforce it explicitly
    os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)
