#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from os import path

from bes.common.check import check
from bes.compat import url_compat
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger
from bes.system.which import which
from bes.system.os_env import os_env
from bes.unix.shell.shell import shell
from bes.unix.sudo.sudo import sudo
from bes.unix.sudo.sudo_cli_options import sudo_cli_options
from bes.url.url_util import url_util

from .brew_error import brew_error

class brew_installer(object):
  'Class to install and uninstall brew on unix.'

  _log = logger('brew_installer')
  
  @classmethod
  def has_brew(clazz):
    'Return True if brew is installed.'

    clazz._check_system()
    return clazz.brew_exe() != None

  @classmethod
  def install(clazz, options):
    'Install brew.'
    check.check_brew_installer_options(options)

    clazz._check_system()
    if clazz.has_brew():
      raise brew_error('brew already installed')
    clazz._do_install(options)
    options.blurber.blurb('Installed brew version {}'.format(clazz.version()))

  @classmethod
  def uninstall(clazz, options):
    'Uninstall brew.'
    check.check_brew_installer_options(options)

    clazz._check_system()
    if not clazz.has_brew():
      raise brew_error('brew not installed')

    clazz.run_script('uninstall.sh', [ '--force' ], options)
    
  @classmethod
  def reinstall(clazz, options):
    'Reinstall brew even if already installed.'
    check.check_brew_installer_options(options)

    clazz._check_system()
    clazz._do_install(options)

  _SUDO_ERROR_MESSAGE = 'Failed to read sudo password for brew.'
  _SUDO_PROMPT = 'sudo password for brew: '
  @classmethod
  def run_script(clazz, script_name, args, options):
    'Download and run a brew script with optional args.'
    check.check_brew_installer_options(options)
    check.check_string(script_name)
    check.check_string_seq(args, allow_none = True)

    if not shell.has_shell('/bin/bash'):
      raise brew_error('/bin/bash is needed to run brew scripts.')

    args = args or []
    tmp_script = clazz.download_script(script_name)

    sudo_options = sudo_cli_options()
    sudo_options.error_message = clazz._SUDO_ERROR_MESSAGE
    sudo_options.prompt = clazz._SUDO_PROMPT
    sudo_options.password = options.password
    clazz._log.log_d('run_script: calling sudo if needed: options={}'.format(options))
    sudo.authenticate_if_needed(options = sudo_options)
    cmd = [ '/bin/bash', tmp_script ] + args
    clazz._log.log_d('run_script: script_name={} cmd={}'.format(script_name, cmd))
    env = os_env.make_clean_env()
    env.update({
      'CI': '1',
    })
    execute.execute(cmd,
                    shell = False,
                    env = env,
                    non_blocking = options.verbose)

  @classmethod
  def _do_install(clazz, options):
    'Install brew.'
    
    clazz._log.log_d('_do_install: calling install.sh options={}'.format(options))
    clazz.run_script('install.sh', [], options)

  @classmethod
  def ensure(clazz, options):
    'Ensure brew is installed.'
    check.check_brew_installer_options(options)

    clazz._check_system()
    if clazz.has_brew():
      options.blurber.blurb('brew already installed at version {}'.format(clazz.version()))
      return
    clazz.install(options)
    
  @classmethod
  def _check_system(clazz):
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
    f = re.findall('^Homebrew\s+(.+)\n', rv.stdout)
    if not f:
      raise brew_error('failed to determine brew version.')
    if len(f) != 1:
      raise brew_error('failed to determine brew version.')
    return f[0]
  
  _BREW_SCRIPT_URL = 'https://raw.githubusercontent.com/Homebrew/install/master/'
  @classmethod
  def _make_script_url(clazz, script):
    'Return the brew exe path.'
    return url_compat.urljoin(clazz._BREW_SCRIPT_URL, script)

  @classmethod
  def download_script(clazz, script_name):
    'Download a brew script to a temp file.'
    check.check_string(script_name)

    url = clazz._make_script_url(script_name)
    tmp = url_util.download_to_temp_file(url, suffix = '-{}'.format(script_name))
    return tmp

  @classmethod
  def call_brew(clazz, args):
    'Call brew.'
    if not clazz.has_brew():
      raise brew_error('brew not installed')
    cmd = [ clazz.brew_exe() ] + args
    return execute.execute(cmd, raise_error = False)
