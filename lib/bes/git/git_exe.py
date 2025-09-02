# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import time

from ..system.check import check
from bes.common.object_util import object_util
from bes.system.which import which
from bes.system.command_line import command_line
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger
from bes.system.os_env import os_env
from bes.text.text_line_parser import text_line_parser

from .git_error import git_error

class git_exe(object):
  'A class to deal with calling git.'

  log = logger('git')

  _DEFAULT_NUM_TRIES = 1
  _DEFAULT_RETRY_WAIT_SECONDS = 1.0
  _MAX_NUM_TRIES = 100
  _MAX_RETRY_WAIT_SECONDS = 60.0 * 10.0 # 10 minutes
  _MIN_RETRY_WAIT_SECONDS = 0.500
  
  @classmethod
  def call_git(clazz, root, args, raise_error = True, extra_env = None,
               num_tries = None, retry_wait_seconds = None):
    check.check_string(root)
    command_line.check_args_type(args)
    check.check_bool(raise_error)
    check.check_dict(extra_env, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)
    check.check_int(num_tries, allow_none = True)
    check.check_float(retry_wait_seconds, allow_none = True)
    #print('args={}'.format(args))
    if isinstance(args, ( list, tuple )):
      parsed_args = list(args)
    else:
      parsed_args = command_line.parse_args(args)
    
    num_tries = num_tries if num_tries != None else clazz._DEFAULT_NUM_TRIES
    retry_wait_seconds = retry_wait_seconds if retry_wait_seconds != None else clazz._DEFAULT_RETRY_WAIT_SECONDS

    if num_tries < 1 or num_tries >= clazz._MAX_NUM_TRIES:
      raise git_error('num_tries should be between 1 and {} instead of "{}"'.format(clazz._DEFAULT_NUM_TRIES,
                                                                                    num_tries))
      
    if retry_wait_seconds < clazz._MIN_RETRY_WAIT_SECONDS or retry_wait_seconds >= clazz._MAX_RETRY_WAIT_SECONDS:
      raise git_error('retry_wait_seconds should be between {} and {} instead of "{}"'.format(clazz._MIN_RETRY_WAIT_SECONDS,
                                                                                              clazz._MAX_RETRY_WAIT_SECONDS,
                                                                                              retry_wait_seconds))
    
    if not hasattr(clazz, '_git_exe'):
      git_exe = clazz.find_git_exe()
      if not git_exe:
        raise git_error('git exe not found in: {}'.format(' '.join(os.environ['PATH'].split(os.pathsep))))
      setattr(clazz, '_git_exe', git_exe)
    git_exe = getattr(clazz, '_git_exe')
    cmd = [ git_exe ] + parsed_args
    clazz.log.log_d('root=%s; cmd=%s' % (root, ' '.join(cmd)))
    extra_env = extra_env or {}
    env = os_env.clone_current_env(d = extra_env, prepend = True)

    last_try_exception = None
    num_failed_attempts = 0
    rv = None
    for i in range(0, num_tries):
      try:
        clazz.log.log_d('call_git: attempt {} of {}: {}'.format(i + 1, num_tries, ' '.join(cmd)))
        rv = execute.execute(cmd, cwd = root, raise_error = False, env = env)
        if rv.exit_code == 0:
          clazz.log.log_i('call_git: success {} of {}: {}'.format(i + 1, num_tries, ' '.join(cmd)))
          break
        else:
          clazz.log.log_i('call_git: failed {} of {}: {}'.format(i + 1, num_tries, ' '.join(cmd)))
          
      except Exception as ex:
        num_failed_attempts += 1
        clazz.log.log_w('call_git: failed {} of {}: {}'.format(i + 1, num_tries, ' '.join(cmd)))
        clazz.log.log_d('call_git: exception: {}'.format(str(ex)))
        clazz.log.log_d('call_git: sleeping {} seconds'.format(retry_wait_seconds))
        time.sleep(retry_wait_seconds)
        last_try_exception = ex

    if not rv:
      message = 'git command attempt failed {} times: {} in {}'.format(num_tries,
                                                                       ' '.join(cmd),
                                                                       root)
      clazz.log.log_w('call_git: {}'.format(message))
      raise git_error(message, execute_result = None)
        
    # first handle the retry failure
    if num_tries > 1 and num_failed_attempts == num_tries and last_try_exception:
      message = 'git command attempt failed {} times: {} in {}\n{}\n{}\n{}'.format(num_tries,
                                                                                   ' '.join(cmd),
                                                                                   root,
                                                                                   str(last_try_exception),
                                                                                   rv.stderr,
                                                                                   rv.stdout)
      clazz.log.log_w('call_git: {}'.format(message))
      raise git_error(message, execute_result = rv)
    
    # handle raise_error if needed
    if rv.exit_code != 0 and raise_error:
      message = 'git command failed: {} in {}\n{}\n{}\n{}'.format(' '.join(cmd),
                                                                  root,
                                                                  str(last_try_exception),
                                                                  rv.stderr,
                                                                  rv.stdout)
      clazz.log.log_w('call_git: {}'.format(message))
      raise git_error(message, execute_result = rv)
    #print('rv={}'.format(rv))
    return rv

  @classmethod
  def find_git_exe(clazz):
    'Return the full path to the git executable.'
    exe_name = clazz._git_exe_name()
    exe = which.which(exe_name)
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

  @classmethod
  def parse_lines(clazz, s):
    return text_line_parser.parse_lines(s, strip_comments = False, strip_text = True, remove_empties = True)
