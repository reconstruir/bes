#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse
from os import path

from bes.common import check
from bes.system import log

from .argparser_handler import argparser_handler

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
    
class command_cli(argparser_handler):

  def __init__(self, log_tag, description, parser = None):
    log.add_logging(self, tag = log_tag)
    if parser:
      self._parser = parser
    else:
      self._parser = argparse.ArgumentParser(description = description)
    super(command_cli, self).__init__(self._parser, log_tag)
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
    
  @classmethod
  def run(clazz):
    raise SystemExit(clazz().main())
