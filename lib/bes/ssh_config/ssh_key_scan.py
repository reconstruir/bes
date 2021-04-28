#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import socket
from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util
from bes.common.tuple_util import tuple_util
from bes.fs.file_util import file_util
from bes.system.command_line import command_line
from bes.system.execute import execute
from bes.system.os_env import os_env
from bes.system.which import which
from bes.text.text_line_parser import text_line_parser

from .ssh_config_error import ssh_config_error
from .ssh_known_host import ssh_known_host

class ssh_key_scan(object):
  'Class to deal with ssh-keyscan'
  
  VALID_KEY_TYPES = ( 'dsa', 'ecdsa', 'ed25519', 'rsa' )
  DEFAULT_KEY_TYPE = 'rsa'
  
  @classmethod
  def scan(clazz, hostname, key_type = None, include_ip_address = True, include_comment = True):
    check.check_string(hostname)
    check.check_string(key_type, allow_none = True)
    check.check_bool(include_ip_address)
    check.check_bool(include_comment)
    
    key_type = key_type or clazz.DEFAULT_KEY_TYPE
    if not clazz.is_valid_key_type(key_type):
      raise ssh_config_error('Invalid key type: "{}"'.format(key_type))
    args = [ '-t', key_type, hostname ]
    output = clazz._call_ssh_keyscan(args)
    result = clazz._parse_ssh_keyscan_output(output, include_comment = include_comment)
    ip_address = socket.gethostbyname(hostname)
    hostname_is_ip = hostname == ip_address
    if hostname_is_ip:
      return result
    if include_ip_address:
      hostnames = result.hostnames + [ ip_address ]
    else:
      hostnames = result.hostnames
    return tuple_util.clone(result, mutations = { 'hostnames': hostnames })

  @classmethod
  def is_valid_key_type(clazz, key_type):
    return key_type in clazz.VALID_KEY_TYPES

  @classmethod
  def _call_ssh_keyscan(clazz, args, cwd = None):
    exe = which.which('ssh-keyscan')
    if not exe:
      raise ssh_config_error('ssh-keyscan executable not found')
    cmd = [ exe ] + command_line.parse_args(args)
    try:
      rv = execute.execute(cmd,
                           env = os_env.make_clean_env(),
                           cwd = cwd,
                           stderr_to_stdout = True)
      return rv.stdout.strip()
    except Exception as ex:
      raise ssh_config_error('Failed to run: "{}" - '.format(' '.join(cmd), str(ex)))

  @classmethod
  def _parse_ssh_keyscan_output(clazz, s, include_comment = True):
    'Parse the output of ssh-keyscan'

    lines = text_line_parser.parse_lines(s, strip_comments = False, strip_text = True, remove_empties = True)
    if len(lines) != 2:
      raise ssh_config_error('Invalid ssh-keyscan output.  Should be 2 lines:\n{}'.format(s))
    comment = lines[0] if include_comment else None
    parts = string_util.split_by_white_space(lines[1], strip = True)
    if len(parts) != 3:
      raise ssh_config_error('Invalid ssh-keyscan parts.  Should be 3 parts: "{}"'.format(lines[1]))
    hostname, key_type, key = parts
    return ssh_known_host([ hostname ], key_type, key, comment)
