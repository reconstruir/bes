#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from bes.computer_setup.computer_setup_task_base import computer_setup_task_base
from bes.macos.command_line_tools.command_line_tools import command_line_tools

class cs_task_command_line_tools(computer_setup_task_base):

  def __init__(self, *args, **kargs):
    super(cs_task_command_line_tools, self).__init__(*args, **kargs)

  #@abstractmethod
  def name(self):
    'Name for task.'
    return 'xcode_command_line_tools'

  #@abstractmethod
  def description(self):
    'Description for task.'
    return 'Install xcode command like tools'

  #@abstractmethod
  def average_duration(self):
    'Average duration in seconds.'
    return 10 * 600

  @abstractmethod
  def is_needed(self):
    'Return True of the task needs to run.'
    return not command_line_tools.installed()
  
  #@abstractmethod
  def run(self):
    'Run the task.'
    command_line_tools.install(self.options.verbose)
