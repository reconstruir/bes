#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from bes.common.check import check
from bes.system.log import logger

from .brew_command import brew_command
from .brew_error import brew_error

class brew(object):
  'Class to deal with unix brew.'

  _log = logger('brew')

  def __init__(self, options):
    self._options = options
    self._command = brew_command()
  
  def has_brew():
    'Return True if brew is installed.'
    self._command.check_system()
    return self._command.has_command()
    
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
    rv = self._command.call_command([ 'formulae', '-1' ])
    return sorted(self._command.split_lines(rv.stdout))

  def installed(self):
    'Return a list of all installed packages.'
    rv = self._command.call_command([ 'list', '-1' ])
    return sorted(self._command.split_lines(rv.stdout))
  
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

    rv = self._command.call_command([ 'list', '-1', package_name ])
    return sorted(self._command.split_lines(rv.stdout))
    
