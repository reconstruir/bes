#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, pprint, time

from bes.common.check import check
from bes.fs.dir_util import dir_util
from bes.fs.file_path import file_path
from bes.fs.file_util import file_util
from bes.system.command_line import command_line
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger
from bes.system.os_env import os_env
from bes.text.text_line_parser import text_line_parser

from .git_clone_options import git_clone_options

class git_basic(object):
  'A class to deal with only the most basic git operations.'

  log = logger('git')
  
  @classmethod
  def remote_origin_url(clazz, root):
    try:
      rv = clazz.call_git(root, [ 'remote', 'get-url', '--push', 'origin' ])
      return rv.stdout.strip()
    except RuntimeError as ex:
      return None
    
  @classmethod
  def init(clazz, root, *args):
    args = [ 'init', '.' ] + list(args or [])
    return clazz.call_git(root, args)

  @classmethod
  def is_repo(clazz, root):
    expected_files = [ 'HEAD', 'config', 'index', 'refs', 'objects' ]
    for f in expected_files:
      if not path.exists(path.join(root, '.git', f)):
        return False
    return True

  @classmethod
  def check_is_git_repo(clazz, d):
    if not clazz.is_repo(d):
      raise RuntimeError('Not a git repo: %s' % (d))
  
  @classmethod
  def call_git(clazz, root, args, raise_error = True, extra_env = None):
    parsed_args = command_line.parse_args(args)
    assert isinstance(parsed_args, list)
    if not hasattr(clazz, '_git_exe'):
      git_exe = clazz.find_git_exe()
      if not git_exe:
        raise RuntimeError('git exe not found.')
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
      #print(message)
      ex = RuntimeError(message)
      setattr(ex, 'execute_result', rv)
      raise ex
    return rv

  @classmethod
  def clone(clazz, address, dest_dir, options = None):
    check.check_git_clone_options(options, allow_none = True)
    address = clazz.resolve_address(address)
    options = options or git_clone_options()
    clazz.log.log_d('clone: address={} dest_dir={} options={}'.format(address, dest_dir, pprint.pformat(options.__dict__)))
    if path.exists(dest_dir):
      if not path.isdir(dest_dir):
        raise RuntimeError('dest_dir %s is not a directory.' % (dest_dir))
      if options.enforce_empty_dir:
        if not dir_util.is_empty(dest_dir):
          raise RuntimeError('dest_dir %s is not empty.' % (dest_dir))
    else:
      file_util.mkdir(dest_dir)
    args = [ 'clone' ]
    if options.depth:
      args.extend([ '--depth', str(options.depth) ])
    args.append(address)
    args.append(dest_dir)
    extra_env = {
      'GIT_LFS_SKIP_SMUDGE': '0' if options.lfs else '1',
    }
    clazz.log.log_d('clone: args="{}" extra_env={}'.format(' '.join(args), extra_env))
    clone_rv = clazz.call_git(os.getcwd(), args, extra_env = extra_env)
    clazz.log.log_d('clone: clone_rv="{}"'.format(str(clone_rv)))
    sub_rv = None
    if options.branch:
      git.checkout(dest_dir, options.branch)
    if options.submodules or options.submodule_list:
      sub_args = [ 'submodule', 'update', '--init' ]
      if options.jobs:
        args.extend([ '--jobs', str(options.jobs) ])
      if options.submodules_recursive:
        sub_args.append('--recursive')
      if options.submodule_list:
        sub_args.extend(options.submodule_list)
      clazz.log.log_d('clone: sub_args="{}" extra_env={}'.format(' '.join(args), extra_env))
      sub_rv = clazz.call_git(dest_dir, sub_args, extra_env = extra_env)
      clazz.log.log_d('clone: sub_rv="{}"'.format(str(sub_rv)))
    return clone_rv, sub_rv

  @classmethod
  def sync(clazz, address, dest_dir, options = None):
    check.check_git_clone_options(options, allow_none = True)
    if clazz.is_repo(dest_dir):
      clazz.checkout(dest_dir, 'master')
    clazz.clone_or_pull(address, dest_dir, options = options)
    branches = clazz.list_branches(dest_dir, 'both')
    for needed_branch in branches.difference:
      clazz.branch_track(dest_dir, needed_branch)
    clazz.call_git(dest_dir, 'fetch --all')
    clazz.call_git(dest_dir, 'pull --all')
  
  @classmethod
  def pull(clazz, root, *args):
    args = [ 'pull', '--verbose' ] + list(args or [])
    return clazz.call_git(root, args)

  @classmethod
  def checkout(clazz, root, revision):
    args = [ 'checkout', revision ]
    return clazz.call_git(root, args)

  @classmethod
  def push(clazz, root, *args):
    args = [ 'push', '--verbose' ] + list(args or [])
    return clazz.call_git(root, args)

  @classmethod
  def push_with_rebase(clazz, root, remote_name = None, num_tries = None, retry_wait_ms = None):
    'Push, but call "pull --rebase origin master" first to be up to date.  With multiple optional retries.'
    check.check_string(root)
    check.check_string(remote_name, allow_none = True)
    check.check_int(num_tries, allow_none = True)
    check.check_float(retry_wait_ms, allow_none = True)

    if check.is_int(num_tries):
      if num_tries <= 0 or num_tries > 100:
        raise ValueError('num_tries should be between 1 and 100: {}'.format(num_tries))
    
    num_tries = num_tries or 1
    save_ex = None
    origin = clazz.remote_origin_url(root) or '<unknown>'
    remote_name = remote_name or 'origin'
    active_branch = clazz.active_branch(root)
    retry_wait_ms = retry_wait_ms or 0.500
    
    pull_command = 'pull --rebase {} {}'.format(remote_name, active_branch)

    clazz.log.log_d('push_with_rebase: num_tries={} pull_command="{}" retry_wait_ms={}'.format(num_tries,
                                                                                               pull_command,
                                                                                               retry_wait_ms))
    for i in range(0, num_tries):
      try:
        clazz.log.log_d('push_with_rebase: attempt {} of {} pushing to {}'.format(i + 1, num_tries, origin))
        clazz.call_git(root, pull_command)
        clazz.push(root)
        clazz.log.log_i('push_with_rebase: success {} of {} pushing to {}'.format(i + 1, num_tries, origin))
        return
      except RuntimeError as ex:
        clazz.log.log_w('push_with_rebase: failed {} of {} pushing to {}'.format(i + 1, num_tries, origin))
        time.sleep(retry_wait_ms)
        save_ex = ex
    raise save_ex

  @classmethod
  def clone_or_pull(clazz, address, dest_dir, options = None):
    if clazz.is_repo(dest_dir):
      if options and options.reset_to_head:
        clazz.reset_to_revision(dest_dir, 'HEAD')
        
      if clazz.has_changes(dest_dir):
        raise RuntimeError('dest_dir %s has changes.' % (dest_dir))

      clazz.pull(dest_dir)

      if options and options.branch:
        clazz.checkout(dest_dir, options.branch)
        clazz.pull(dest_dir)
      
    else:
      clazz.clone(address, dest_dir, options = options)
  
  @classmethod
  def short_hash(clazz, root, long_hash):
    args = [ 'rev-parse', '--short', long_hash ]
    rv = clazz.call_git(root, args)
    return rv.stdout.strip()

  @classmethod
  def long_hash(clazz, root, short_hash):
    args = [ 'rev-parse', short_hash ]
    rv = clazz.call_git(root, args)
    return rv.stdout.strip()
  
  @classmethod
  def root(clazz, filename):
    'Return the repo root for the given filename or raise and exception if not under git control.'
    cmd = [ 'git', 'rev-parse', '--show-toplevel' ]
    if path.isdir(filename):
      cwd = filename
    else:
      cwd = path.dirname(filename)
    rv = execute.execute(cmd, cwd = cwd, raise_error = False)
    if rv.exit_code != 0:
      return None
    l = clazz.parse_output_lines(rv.stdout)
    assert len(l) == 1
    return l[0]
  
  @classmethod
  def is_tracked(clazz, root, filename):
    'Return True if the filename is tracked by a git repo.'
    args = [ 'ls-files', '--error-unmatch', filename ]
    return clazz.call_git(root, args, raise_error = False).exit_code == 0
  
  @classmethod
  def parse_output_lines(clazz, s):
    return text_line_parser.parse_lines(s, strip_comments = False, strip_text = True, remove_empties = True)
    
  @classmethod
  def where_is_valid(clazz, where):
    return where in [ 'local', 'remote', 'both' ]

  @classmethod
  def check_where(clazz, where):
    if not clazz.where_is_valid(where):
      raise ValueError('where should be local, remote or both instead of: {}'.format(where))
    return where

  @classmethod
  def determine_where(clazz, local, remote, default_value = 'both'):
    if local is None and remote is None:
      return default_value
    local = bool(local)
    remote = bool(remote)
    if local and remote:
      return 'both'
    elif local:
      return 'local'
    elif remote:
      return 'remote'
    assert False
    
  @classmethod
  def resolve_address(clazz, address):
    'If address is a local dir, return its absolute path with ~ expanded.  Otherwise just return address.'
    resolved_address = path.expanduser(address)
    if path.isdir(resolved_address):
      return resolved_address
    return address

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

  @classmethod
  def _is_valid_hash_char(clazz, c):
    'Return True if c is a valid git hash char.'
    return (c >= 'a' and c <= 'f') or (c >= '0' and c <= '9')

  @classmethod
  def _is_valid_hash(clazz, h):
    for c in h:
      if not clazz._is_valid_hash_char(c):
        return False
    return True
  
  @classmethod
  def is_long_hash(clazz, h):
    'Return True if h is a valid git long hash.'
    return len(h) == 40 and clazz._is_valid_hash(h)

  @classmethod
  def is_short_hash(clazz, h):
    'Return True if h is a valid git short hash.'
    return len(h) == 7 and clazz._is_valid_hash(h)

  @classmethod
  def is_hash(clazz, h):
    'Return True if h is a valid short long git hash.'
    return len(h) in [ 7, 40 ] and clazz._is_valid_hash(h)
