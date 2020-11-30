#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from bes.common.check import check
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger
from bes.system.which import which

from .brew_error import brew_error

class brew(object):
  'Class to install and uninstall brew on unix.'

  _log = logger('brew')
  
  @classmethod
  def has_brew(clazz):
    'Return True if brew is installed.'

    clazz.check_system()
    return clazz.brew_exe() != None
    
  @classmethod
  def check_system(clazz):
    if host.SYSTEM in [ host.MACOS, host.LINUX ]:
      return
    raise brew_error('brew is only for macos or linux: "{}"'.format(host.SYSTEM))

  @classmethod
  def brew_exe(clazz):
    'Return the brew exe path.'
    return which.which('brew')

  @classmethod
  def version(clazz):
    'Return the version of brew.'
    if not clazz.has_brew():
      raise brew_error('brew not installed')
    rv = clazz.call_brew([ '--version' ])
    f = re.findall(r'^Homebrew\s+(.+)\n', rv.stdout)
    if not f:
      raise brew_error('failed to determine brew version.')
    if len(f) != 1:
      raise brew_error('failed to determine brew version.')
    return f[0]

  @classmethod
  def call_brew(clazz, args):
    'Call brew.'
    if not clazz.has_brew():
      raise brew_error('brew not installed')
    cmd = [ clazz.brew_exe() ] + args
    return execute.execute(cmd, raise_error = False)
