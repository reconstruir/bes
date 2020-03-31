# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#from bes.common.check import check
import os.path as path

from bes.common.check import check
from bes.common.string_util import string_util
from bes.compat.StringIO import StringIO

from .git_error import git_error

class git_address_util(object):
  'Misc functions to deal with git addresses.'

  @classmethod
  def resolve(clazz, address):
    'If address is a local dir, return its absolute path with ~ expanded.  Otherwise just return address.'
    check.check_string(address)
    
    resolved_address = path.expanduser(address)
    if path.isdir(resolved_address):
      return resolved_address
    return address
  
  @classmethod
  def name(clazz, address):
    check.check_string(address)

    address = clazz.resolve(address)
    if path.isdir(address):
      return path.basename(address)
    if not address.endswith('.git'):
      raise git_error('Not a git address: "{}"'.format(address))
    buf = StringIO()
    for c in string_util.reverse(address):
      if c in ':/':
        break
      buf.write(c)
    last_part = string_util.reverse(buf.getvalue())
    return string_util.remove_tail(last_part, '.git')

  @classmethod
  def sanitize_for_local_path(clazz, address):
    'Return a local path sanitized from an address.  Suitable for local caching of remote git stuff.'
    check.check_string(address)

    return string_util.replace(address, { ':': '_', '/': '_' })
