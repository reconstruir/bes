#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.which import which
from bes.system.execute import execute
from bes.system.log import logger

from bes.native_package.native_package import native_package
from bes.macos.softwareupdater.softwareupdater import softwareupdater

from .command_line_tools_error import command_line_tools_error
from .command_line_tools_force import command_line_tools_force

class command_line_tools(object):
  'Class to deal with the command_line_tools executable.'

  _log = logger('command_line_tools')
  
  @classmethod
  def installed(clazz, verbose = False):
    'Return True if command line tools are installed.'

    exe = which.which('xcode-select')
    if not exe:
      return False

    cmd = [ exe, '--print-path' ]
    rv = execute.execute(cmd, raise_error = False)
    if rv.exit_code != 0:
      if verbose:
        print('not installed')
      return False
    print('installed')
    return True
  
  @classmethod
  def install(clazz, verbose):
    'Install the command line tools.'

    installed = clazz.installed(False)
    clazz._log.log_i('install: installed={}'.format(installed))
    if installed:
      raise command_line_tools_error('command line tools already installed.')

    with command_line_tools_force(force = True) as force:
      available_updates = softwareupdater.available()
      clazz._log.log_i('install: available_updates={}'.format(available_updates))
      for next_update in available_updates:
        clazz._log.log_i('install: next_update={}'.format(next_update))
        if 'command line tools' in next_update.title.lower():
          print('installing: {}'.format(next_update.label))
          softwareupdater.install(next_update.label, verbose)
    
  @classmethod
  def ensure(clazz, verbose):
    'Ensure that the command line tools are installed.'

    if clazz.installed(False):
      return
    clazz.install(verbose)
