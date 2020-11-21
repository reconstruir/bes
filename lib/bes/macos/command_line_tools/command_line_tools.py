#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.system.which import which
from bes.system.execute import execute

from bes.native_package.native_package import native_package
from bes.macos.softwareupdater.softwareupdater import softwareupdater

from .command_line_tools_error import command_line_tools_error
from .command_line_tools_force import command_line_tools_force

class command_line_tools(object):
  'Class to deal with the command_line_tools executable.'
  
  @classmethod
  def installed(clazz, verbose):
    'Return True of command line tools are installed.'

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

    if clazz.installed(verbose):
      raise command_line_tools_error('command line tools already installed.')

    with command_line_tools_force() as force:
      available_update = softwareupdater.available()
      for next_update in available_update:
        if next_update.title == 'Command Line Tools for Xcode':
          print('installing: {}'.format(next_update.label))
          softwareupdater.install(next_update.label, verbose)
    
  @classmethod
  def ensure(clazz, verbose):
    'Ensure that the command line tools are installed.'

    if clazz.installed(False):
      return
    clazz.install(verbose)
