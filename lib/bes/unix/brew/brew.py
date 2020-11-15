#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from os import path

from bes.system.host import host
from bes.system.which import which
from bes.system.execute import execute
from bes.url.url_util import url_util
from bes.compat import url_compat
from bes.common.check import check
from bes.unix.shell.shell import shell
from bes.unix.sudo.sudo_exe import sudo_exe

from .brew_error import brew_error

class brew(object):
  'Class to deal with brew on macos.'

  @classmethod
  def has_brew(clazz):
    'Return True if brew is installed.'

    clazz._check_system()
    return clazz._brew_exe() != None

  @classmethod
  def install(clazz, verbose):
    'Install brew.'
    check.check_bool(verbose)

    clazz._check_system()
    if clazz.has_brew():
      raise brew_error('brew already installed')
    clazz._do_install(verbose)

  @classmethod
  def uninstall(clazz, verbose):
    'Uninstall brew.'
    check.check_bool(verbose)

    clazz._check_system()
    if not clazz.has_brew():
      raise brew_error('brew not installed')

    clazz.run_script('uninstall.sh', [ '--force' ], verbose)
    
  @classmethod
  def reinstall(clazz, verbose):
    'Reinstall brew even if already installed.'
    check.check_bool(verbose)

    clazz._check_system()
    clazz._do_install(verbose)

  _SUDO_ERROR_MESSAGE = 'Failed to read sudo password for brew hackery.'
  _SUDO_PROMPT = 'sudo password for brew hackery: '
  @classmethod
  def run_script(clazz, script_name, args, verbose):
    'Download and run a brew script with optional args.'
    check.check_string(script_name)
    check.check_string_seq(args, allow_none = True)
    check.check_bool(verbose)
    
    if not shell.has_shell('/bin/bash'):
      raise brew_error('/bin/bash is needed to run brew scripts.')

    args = args or []
    tmp_script = clazz.download_script(script_name)

    sudo_exe.authenticate_if_needed(msg = clazz._SUDO_ERROR_MESSAGE,
                                    prompt = clazz._SUDO_PROMPT)
    
    cmd = [ '/bin/bash', tmp_script ] + args
    execute.execute(cmd, shell = False, non_blocking = verbose)

  @classmethod
  def _do_install(clazz, verbose):
    'Install brew.'

    clazz.run_script('install.sh', [], verbose)

  @classmethod
  def ensure(clazz, verbose):
    'Ensure brew is installed.'

    clazz._check_system()
    if clazz.has_brew():
      return
    clazz.install(verbose)
    
  @classmethod
  def _check_system(clazz):
    if host.SYSTEM in [ host.MACOS, host.LINUX ]:
      return
    raise brew_error('brew is only for macos or linux: "{}"'.format(host.SYSTEM))

  @classmethod
  def _brew_exe(clazz):
    'Return the brew exe path.'
    return which.which('brew')

  @classmethod
  def version(clazz):
    'Return the version of brew.'
    if not clazz.has_brew():
      raise brew_error('brew not installed')
    rv = execute.execute([ clazz._brew_exe(), '--version' ])
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
