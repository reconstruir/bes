#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.common.json_util import json_util
from bes.compat.plistlib import plistlib_loads
from bes.fs.temp_file import temp_file
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger

from .defaults_error import defaults_error

class defaults(object):
  'Class to deal with the macos defaults program.'

  _log = logger('defaults')
  
  @classmethod
  def get_domain(clazz, domain, style):
    'Return a list of available software update items.'
    check.check_string(domain)
    check.check_string(style)

    if not style in [ 'json', 'raw', 'plist' ]:
      raise defaults_error('style should be one of json, raw or plist: "{}"'.format(style))

    host.check_is_macos()

    if style == 'json':
      return clazz._get_domain_json(domain)
    elif style == 'plist':
      return clazz._get_domain_plist(domain)
    elif style == 'raw':
      return clazz._get_domain_raw(domain)

  @classmethod
  def get_value(clazz, domain, key):
    'Get a value.'
    check.check_string(domain)
    check.check_string(key)

    host.check_is_macos()
    
    o = clazz._get_domain_object(domain)
    if not key in o:
      raise defaults_error('key "{}" not found in domain "{}"'.format(key, domain))
    return o[key]

  @classmethod
  def set_value(clazz, domain, key, value):
    'Set a value.'
    check.check_string(domain)
    check.check_string(key)
    check.check_string(value)

    host.check_is_macos()
    
    cmd = [ 'defaults', '-currentHost', 'write', domain, key, value ]
    rv = execute.execute(cmd, raise_error = False)
    if rv.exit_code != 0:
      cmd_flat = ' '.join(cmd)
      msg = 'defaults command failed: {} - {}\n{}'.format(cmd_flat,
                                                          rv.exit_code,
                                                          rv.stdout)
      raise defaults_error(msg, status_code = rv.exit_code)
  
  @classmethod
  def _get_domain_raw(clazz, domain):
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
  def _get_domain_plist(clazz, domain):
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
  def _get_domain_object(clazz, domain):
    plist = clazz._get_domain_plist(domain)
    return plistlib_loads(plist)
  
  @classmethod
  def _get_domain_json(clazz, domain):
    o = clazz._get_domain_object(domain)
    return json_util.normalize(o)
