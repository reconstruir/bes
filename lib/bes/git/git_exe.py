# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.common.check import check
from bes.fs.file_path import file_path
from bes.system.command_line import command_line
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger
from bes.system.os_env import os_env

from .git_error import git_error

class git_exe(object):
  'A class to deal with calling git.'

  log = logger('git')

  @classmethod
  def call_git(clazz, root, args, raise_error = True, extra_env = None):
    parsed_args = command_line.parse_args(args)
    assert isinstance(parsed_args, list)
    if not hasattr(clazz, '_git_exe'):
      git_exe = clazz.find_git_exe()
      if not git_exe:
        raise git_error('git exe not found in: {}'.format(' '.join(os.environ['PATH'].split(os.pathsep))))
      setattr(clazz, '_git_exe', git_exe)
    git_exe = getattr(clazz, '_git_exe')
    cmd = [ git_exe ] + parsed_args
    clazz.log.log_d('root=%s; cmd=%s' % (root, ' '.join(cmd)))
    save_raise_error = raise_error
    extra_env = extra_env or {}
    env = os_env.clone_current_env(d = extra_env, prepend = True)
    rv = execute.execute(cmd, cwd = root, raise_error = False, env = env)
    if rv.exit_code != 0 and save_raise_error:
      message = 'git command failed: %s in %s\n' % (' '.join(cmd), root)
      message += rv.stderr
      message += rv.stdout
      # print(message)
      raise git_error(message, execute_result = rv)
    return rv

  @classmethod
  def find_git_exe(clazz):
    'Return the full path to the git executable.'
    exe_name = clazz._git_exe_name()
    exe = file_path.which(exe_name)
    return exe

  @classmethod
  def _git_exe_name(clazz):
    'Return the platform specific name of the git exe.'
    if host.is_unix():
      return 'git'
    elif host.is_windows():
      return 'git.exe'
    else:
      host.raise_unsupported_system()
