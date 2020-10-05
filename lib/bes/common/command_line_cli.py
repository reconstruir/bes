#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect

from bes.common.inspect_util import inspect_util

class command_line_cli(object):
  'command line'

  def __init__(self, name):
    self._name = name

  def run(self):
    commands = self._get_command_methods()
    for command in commands:
      name = command[0]
      desc = command[1]
      argspec = inspect_util.getargspec(desc)
#      help(desc)
      print("desc: ", desc, type(desc))
      print("args: ", argspec, type(argspec))
      
    return 0

  @classmethod
  def _get_command_methods(self):
    def is_command(command):
      return inspect.ismethod(command) # and x[0].startswith('command'))
    methods = inspect.getmembers(self, predicate = inspect.ismethod)
    return [ m for m in methods if m[0].startswith('command_') ]
