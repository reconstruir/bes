#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import json
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
    return self._command.call_command_parse_lines([ 'list', '--formulae', '-1' ], sort = True)
  
  def uninstall(self, package_name):
    'Uninstall a package.'
    check.check_string(package_name)
    
    self._command.call_command([ 'uninstall', package_name ])

  def install(self, package_name):
    'Install a package.'
    check.check_string(package_name)
    
    self._command.call_command([ 'install', package_name ])

  def upgrade(self, package_name):
    'Upgrade a package.  Returns True if it updated.'
    check.check_string(package_name)

    cmd = [ 'upgrade', package_name ]
    self._command.call_command(cmd)
    
  def files(self, package_name):
    'Return a list of files for a package.'
    check.check_string(package_name)

    return self._command.call_command_parse_lines([ 'list', '-1', package_name ], sort = True)

  def update(self):
    'Update brew to get the lastes package defininitions.'
    self._command.call_command([ 'update' ])
    
  _outdated_package = namedtuple('_outdated_package', 'name, installed_versions, latest_version')
  def outdated(self):
    'Return a dictionary of outdated packages'
    self.update()
    cmd = [ 'outdated', '--json' ]
    rv = self._command.call_command(cmd)
    outdated = json.loads(rv.stdout)
    result = {}
    for next_item in outdated['formulae']:
      op = self._outdated_package(next_item['name'],
                                  next_item['installed_versions'],
                                  next_item['current_version'])
      result[op.name] = op
    return result

  _needs_update_result = namedtuple('_needs_update_result', 'needs_update, info')
  def needs_update(self, package_name):
    'Return a dictionary of outdated packages'
    check.check_string(package_name)

    if not package_name in self.installed():
      return self._needs_update_result(True, None)
    
    self.update()
    cmd = [
      'outdated',
      '--json',
      package_name,
    ]
    rv = self._command.call_command(cmd, raise_error = False)
    if rv.exit_code == 0:
      return self._needs_update_result(False, None)
    if rv.stderr:
      raise brew_error('failed to determine if "{}" needs update - {}'.format(package_name, rv.stderr))
    outdated = json.loads(rv.stdout)
    assert 'formulae' in outdated
    formulae = outdated['formulae']
    assert len(formulae) == 1
    item = formulae[0]
    info = self._outdated_package(item['name'],
                                  item['installed_versions'],
                                  item['current_version'])
    return self._needs_update_result(True, info)
