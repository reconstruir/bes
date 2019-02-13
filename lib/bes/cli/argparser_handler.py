#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect
from bes.system import logger

from bes.common import check
from bes.system import log
from bes.fs import file_check
from bes.git import git

class argparser_handler(object):
  'A class to simplify the process of calling functions to handler argparser command'
  
  def __init__(self, parser, log_tag):
    self._log_tag = log_tag
    self._parser = parser

  def main(self):
    log = logger(self._log_tag)
    args = self._parser.parse_args()
    if hasattr(args, 'sub_command'):
      command = '%s_%s' % (args.command, args.sub_command)
    else:
      command = args.command
    log.log_d('command=%s' % (command))
    method_name = '_command_%s' % (command)
    handler = getattr(self, method_name, None)
    if not handler:
      raise RuntimeError('No method found for command: %s' % (method_name))
    arg_names = inspect.getargspec(handler).args
    if arg_names[0] != 'self':
      raise RuntimeError('First argument should be \"self\": %s' (method_name))
    arg_names.pop(0)
    args = [ getattr(args, arg_name) for arg_name in arg_names ]
    args_blurb = '; '.join([ '%s=%s' % (key, value) for ( key, value ) in zip(arg_names, args) ])
    log.log_d('calling %s(%s)' % (method_name, args_blurb))
    exit_code = handler(*args)
    if not isinstance(exit_code, int):
      raise RuntimeError('Handler should return an int exit_code: %s' % (handler))
    log.log_d('%s() returns %d' % (method_name, exit_code))
    return exit_code

  @classmethod
  def check_file(clazz, filename):
    file_check.check_file(filename)

  @classmethod
  def check_dir(clazz, dirname):
    file_check.check_dir(dirname)

  @classmethod
  def check_dir_is_git_repo(clazz, d):
    git.check_is_git_repo(d)

  @classmethod
  def resolve_file(clazz, filename, root_dir = None):
    '''
    Resolve a filename as follows:
     . expand ~ to $HOME
     . make it an absolute path
    '''
    if root_dir:
      filename = path.join(root_dir, filename)
    else:
      if '~' in filename:
        filename = path.expanduser(filename)
      if not path.isabs(filename):
        filename = path.abspath(filename)
    return filename

  @classmethod
  def resolve_dir(clazz, dirname, root_dir = None):
    return clazz.resolve_file(dirname, root_dir = root_dir)
  
