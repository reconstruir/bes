#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from bes.common.check import check
from bes.system.log import logger

from .brew_command import brew_command
from .brew_error import brew_error
from .brew_options import brew_options

class brew(object):
  'Class to deal with unix brew.'

  _log = logger('brew')

  def __init__(self, options = None):
    self._options = options or brew_options()
    self._command = brew_command()

  @classmethod
  def has_brew(clazz):
    'Return True if brew is supported and installed.'
    return brew_command().has_command()
    
  def version(self):
    'Return the version of brew.'

    rv = self._command.call_command([ '--version' ])
    f = re.findall(r'^Homebrew\s+(.+)\n', rv.stdout)
    if not f:
      raise brew_error('failed to determine brew version.')
    if len(f) != 1:
      raise brew_error('failed to determine brew version.')
    return f[0]

  def available(self):
    'Return a list of all available packages.'
    return self._command.call_command_parse_lines([ 'formulae', '-1' ], sort = True)

  def installed(self):
    'Return a list of all installed packages.'
    return self._command.call_command_parse_lines([ 'list', '-1' ], sort = True)
  
  def uninstall(self, package_name):
    'Uninstall a package.'
    check.check_string(package_name)
    
    self._command.call_command([ 'uninstall', package_name ])

  def install(self, package_name):
    'Install a package.'
    check.check_string(package_name)
    
    self._command.call_command([ 'install', package_name ])

  def files(self, package_name):
    'Return a list of files for a package.'
    check.check_string(package_name)

    return self._command.call_command_parse_lines([ 'list', '-1', package_name ], sort = True)
    
