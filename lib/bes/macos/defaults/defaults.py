#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.common.json_util import json_util
from bes.common.object_util import object_util
from bes.system.command_line import command_line
from bes.fs.temp_file import temp_file
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger
from bes.system.os_env import os_env
from bes.system.which import which
from bes.text.tree_text_parser import tree_text_parser
from bes.text.text_line_parser import text_line_parser

from .defaults_item import defaults_item
from .defaults_error import defaults_error

from bes.compat.plistlib import plistlib_loads

class defaults(object):
  'Class to deal with the macos softwareupdate program.'

  _log = logger('defaults')
  
  @classmethod
  def read_domain(clazz, domain, style):
    'Return a list of available software update items.'
    check.check_string(domain)
    check.check_string(style)

    if not style in [ 'json', 'raw', 'plist' ]:
      raise defaults_error('style should be one of json, raw or plist: "{}"'.format(style))

    host.check_is_macos()

    if style == 'json':
      return clazz._read_domain_json(domain)
    elif style == 'plist':
      return clazz._read_domain_plist(domain)
    elif style == 'raw':
      return clazz._read_domain_raw(domain)

  @classmethod
  def _convert_plist_to_json(clazz, content):
    tmp = temp_file.make_temp_file(content = content, suffix = '.plist', delete = False)
    convert_cmd = [ 'plutil', '-convert', 'json', '-o', '-', tmp ]
    rv = execute.execute(convert_cmd, raise_error = False)
    if rv.exit_code != 0:
      cmd_flat = ' '.join(convert_cmd)
      msg = 'failed to convert plist to json: {} - {}\n{}'.format(cmd_flat,
                                                                  rv.exit_code,
                                                                  rv.stdout)
    return rv.stdout
#    return json_util.normalize_text(rv.stdout)

  @classmethod
  def _read_domain_raw(clazz, domain):
    cmd = [ 'defaults', '-currentHost', 'read' ]
    rv = execute.execute(cmd, raise_error = False)
    if rv.exit_code != 0:
      cmd_flat = ' '.join(cmd)
      msg = 'defaults command failed: {} - {}\n{}'.format(cmd_flat,
                                                          rv.exit_code,
                                                          rv.stdout)
      raise defaults_error(msg, status_code = rv.exit_code)
    return rv.stdout

  @classmethod
  def _read_domain_plist(clazz, domain):
    cmd = [ 'defaults', '-currentHost', 'export', domain, '-' ]
    rv = execute.execute(cmd, raise_error = False)
    if rv.exit_code != 0:
      cmd_flat = ' '.join(cmd)
      msg = 'defaults command failed: {} - {}\n{}'.format(cmd_flat,
                                                          rv.exit_code,
                                                          rv.stdout)
      raise defaults_error(msg, status_code = rv.exit_code)
    return rv.stdout
  
  @classmethod
  def _read_domain_json(clazz, domain):
    plist = clazz._read_domain_plist(domain)
    pi = plistlib_loads(plist)
    return json_util.normalize(pi)
