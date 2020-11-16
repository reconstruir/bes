#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import tempfile

from bes.common.check import check
from bes.common.object_util import object_util
from bes.system.command_line import command_line
from bes.system.execute import execute
from bes.system.log import logger
from bes.system.os_env import os_env
from bes.system.which import which

from .sudo_cli_options import sudo_cli_options
from .sudo_error import sudo_error

class sudo_exe(object):
  'Class to deal with the sudo_exe executable.'

  _log = logger('sudo')
  
  @classmethod
  def call_sudo(clazz, args, options = None, msg = None):
    check.check_sudo_cli_options(options, allow_none = True)
    check.check_string(msg, allow_none = True)

    command_line.check_args_type(args)
    args = object_util.listify(args)
    #    parsed_args = command_line.parse_args(args)
    options = options or sudo_cli_options()

    exe = which.which('sudo')
    if not exe:
      raise sudo_error('sudo not found')
    
    clazz._log.log_d('sudo_exe: exe={} args={} options={} msg={}'.format(exe,
                                                                         args,
                                                                         options,
                                                                         msg))
    
    cmd = [ exe ]
#    if password:
#      input_data = password
#      cmd.append('--stdin')
    if options.prompt:
      cmd.extend( [ '--prompt', '"{}"'.format(options.prompt) ] )
    cmd.extend(args)
    env = os_env.clone_current_env(d = {})
    rv = execute.execute(cmd,
                         env = env,
                         cwd = options.working_dir,
                         stderr_to_stdout = True,
                         raise_error = False,
                         non_blocking = options.verbose)
    if rv.exit_code != 0:
      if not msg:
        cmd_flag = ' '.join(cmd)
        msg = 'sudo_exe command failed: {}\n{}'.format(cmd_flag, rv.stdout)
      raise sudo_error(msg)
    return rv

#options = None, msg = None
  
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
  def authenticate_if_needed(clazz, cwd = None, msg = None, prompt = 'sudo password: ', password = None):
    'Authenticate only if needed'
    if clazz.is_authenticated(cwd = cwd, password = password):
      return
    clazz.authenticate(cwd = cwd, msg = msg, prompt = prompt, password = password)
    
  @classmethod
  def is_authenticated(clazz, cwd = None, password = None):
    'Return True if the user is already sudo authenticated.'
    try:
      clazz.call_sudo('--non-interactive true',
                      cwd = tempfile.gettempdir(),
                      password = password)
      return True
    except sudo_error as ex:
      pass
    return False
