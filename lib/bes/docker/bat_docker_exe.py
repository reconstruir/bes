#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.system.os_env import os_env
from bes.system.which import which
from bes.system.command_line import command_line
from bes.system.execute import execute

from .bat_docker_error import bat_docker_error

class bat_docker_exe(object):
  'Class to deal with the docker executable.'
  
  @classmethod
  def call_docker(clazz, args, cwd = None, non_blocking = True, shell = False):
    exe = which.which('docker')
    if not exe:
      raise bat_docker_error('docker not found')
    cmd = [ exe ] + command_line.parse_args(args)
    env = os_env.clone_current_env(d = {})
    rv = execute.execute(cmd,
                         env = env,
                         shell = shell,
                         cwd = cwd,
                         stderr_to_stdout = True,
                         non_blocking = non_blocking,
                         raise_error = False)
    if rv.exit_code != 0:
      cmd_flag = ' '.join(cmd)
      msg = 'docker command failed: {}\n{}'.format(cmd_flag, rv.stdout)
      raise bat_docker_error(msg)
    return rv
