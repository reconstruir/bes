#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, inspect, os
from os import path

from bes.common import check
from bes.fs import file_util
from bes.system import log
from bes.git import git

class _command(object):

  def __init__(self, name, parser):
    check.check_string(name)
    self._parser = parser
    self._name = name
    self._arguments = []
    
  def add_argument(self, *args, **kargs):
    arg = self._parser.add_argument(*args, **kargs)
    self._arguments.append(arg)

  def arg_names(self):
    return [ arg.dest for arg in self._arguments ]
    
class command_cli(object):

  def __init__(self, log_tag, description, parser = None):
    log.add_logging(self, tag = log_tag)
    if parser:
      self._parser = parser
    else:
      self._parser = argparse.ArgumentParser(description = description)
    self._command_parser = self._parser.add_subparsers(help = 'commands', dest = 'command')
    self._commands = {}
    
  def add_command(self, name, help_blurb):
    assert not name in self._commands
    command_parser = self._command_parser.add_parser(name, help = help_blurb)
    self._commands[name] = _command(name, command_parser)

  def add_argument(self, name, *args, **kargs):
    if not name in self._commands:
      raise RuntimeError('Unknown command: %s' % (name))
      
    command = self._commands[name]
    command.add_argument(*args, **kargs)
    
  def main(self):
    args = self._parser.parse_args()
    if not args.command in self._commands:
      raise RuntimeError('Unknown command: %s' % (args.command))
    command = self._commands[args.command]

    method_name = '_command_%s' % (args.command)
    if not hasattr(self, method_name):
      raise RuntimeError('No method found for command: %s' % (method_name))

    handler = getattr(self, method_name)
    arg_names = command.arg_names()
    args = [ getattr(args, arg_name) for arg_name in arg_names ]
    blurb = '; '.join([ '%s=%s' % (key, value) for ( key, value ) in zip(arg_names, args) ])
    self.log_d('%s: %s' % (method_name, blurb))
    exit_code = handler(*args)
    if not isinstance(exit_code, int):
      raise RuntimeError('Handler should return an int exit_code: %s' % (handler))
    return exit_code

  @classmethod
  def run(clazz):
    raise SystemExit(clazz().main())

  @classmethod
  def check_file_exists(clazz, filename, label = 'file'):
    if not path.isfile(filename):
      raise RuntimeError('%s not found: %s' % (label, filename))

  @classmethod
  def check_dir_exists(clazz, d, label = 'dir'):
    if not path.isdir(d):
      raise RuntimeError('%s not found: %s' % (label, d))

  @classmethod
  def check_dir_is_git_repo(clazz, d):
    git.check_is_git_repo(d)

  @classmethod
  def resolve_filename(clazz, f, root_dir = None):
    '''
    Resolve a filename as follows:
     . expand ~ to $HOME
     . make it an absolute path
    '''
    if root_dir:
      f = path.join(root_dir, f)
    else:
      if '~' in f:
        f = path.expanduser(f)
      if not path.isabs(f):
        f = path.abspath(f)
    return f

  @classmethod
  def resolve_dir(clazz, f, root_dir = None):
    return clazz.resolve_filename(f, root_dir = root_dir)
