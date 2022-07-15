#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import tempfile

from bes.system.check import check
from bes.common.object_util import object_util
from bes.system.command_line import command_line
from bes.system.execute import execute
from bes.system.log import logger
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.os_env import os_env
from bes.system.which import which

from .sudo_cli_options import sudo_cli_options
from .sudo_error import sudo_error

class sudo(object):
  'Class to deal with the sudo executable.'

  _log = logger('sudo')
  
  @classmethod
  def call_sudo(clazz, args, options = None):
    check.check_sudo_cli_options(options, allow_none = True)

    command_line.check_args_type(args)
    args = object_util.listify(args)
    options = options or sudo_cli_options()

    exe = which.which('sudo')
    if not exe:
      raise sudo_error('sudo not found')
    
    clazz._log.log_d('sudo: exe={} args={} options={}'.format(exe,
                                                                  args,
                                                                  options))
    
    cmd = [ exe ]
    tmp_askpass = None
    askpass_env = {}
    if options.password:
      tmp_askpass = clazz._make_temp_askpass(options.password)
      askpass_env = { 'SUDO_ASKPASS': tmp_askpass }
      cmd.append('--askpass')
    if options.prompt:
      cmd.extend( [ '--prompt', '"{}"'.format(options.prompt) ] )
    cmd.extend(args)
    env = os_env.clone_current_env(d = askpass_env)
    try:
      rv = execute.execute(cmd,
                           env = env,
                           cwd = options.working_dir,
                           stderr_to_stdout = True,
                           raise_error = False,
                           non_blocking = options.verbose)
      if rv.exit_code != 0:
        if options.error_message:
          msg = options.error_message
        else:
          cmd_flat = ' '.join(cmd)
          msg = 'sudo command failed: {}\n{}'.format(cmd_flat, rv.stdout)
        raise sudo_error(msg)
      return rv
    finally:
      if tmp_askpass:
        file_util.remove(tmp_askpass)
  
  @classmethod
  def authenticate(clazz, options = None):
    'Authenticate the user by prompting for sudo password *if* needed'
    check.check_sudo_cli_options(options, allow_none = True)
    args = [ '--validate' ]
    if options and options.force_auth:
      args.append('--reset-timestamp')
    clazz.call_sudo(args, options = options)

  @classmethod
  def reset(clazz, options = None):
    'Reset the authenticatation'
    check.check_sudo_cli_options(options, allow_none = True)

    clazz.call_sudo('--reset-timestamp', options = options)
    
  @classmethod
  def authenticate_if_needed(clazz, options = None):
    'Authenticate only if needed'
    if clazz.is_authenticated(options = options):
      print('already')
      return
    clazz.authenticate(options = options)
    
  @classmethod
  def is_authenticated(clazz, options):
    'Return True if the user is already sudo authenticated.'
    try:
      clazz.call_sudo('--non-interactive true', options = options)
      return True
    except sudo_error as ex:
      pass
    return False

  @classmethod
  def _make_temp_askpass(clazz, password):
    content = '''\
#!/bin/sh
echo "{password}"
'''.format(password = password)
    return temp_file.make_temp_file(content = content, delete = True, perm = 0o700)
