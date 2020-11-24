#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from bes.computer_setup.computer_setup_task import computer_setup_task

from bes.unix.brew.brew import brew
from bes.unix.shell.shell import shell

class cst_change_shell_to_bash(computer_setup_task):

  def __init__(self, *args, **kargs):
    super(cst_change_shell_to_bash, self).__init__(*args, **kargs)

  #@abstractmethod
  def name(self):
    'Name for task.'
    return 'change_shell_to_bash'

  #@abstractmethod
  def description(self):
    'Description for task.'
    return 'Change the shell to bash'

  #@abstractmethod
  def average_duration(self):
    'Average duration in seconds.'
    return 0

  @abstractmethod
  def is_needed(self):
    'Return True of the task needs to run.'
    return not shell.shell_is_bash()
  
  #@abstractmethod
  def run(self, *args, **kwargs):
    'Run the task.'
    shell.change_shell('/bin/bash', self.options.password)
