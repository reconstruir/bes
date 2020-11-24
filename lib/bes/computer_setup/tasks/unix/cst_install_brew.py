#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from bes.computer_setup.computer_setup_task import computer_setup_task

from bes.unix.brew.brew import brew
from bes.unix.brew.brew_cli_options import brew_cli_options

class cst_install_brew(computer_setup_task):

  #@abstractmethod
  def name(self):
    'Name for task.'
    return 'install_brew'

  #@abstractmethod
  def description(self):
    'Description for task.'
    return 'Install brew'

  #@abstractmethod
  def average_duration(self):
    'Average duration in seconds.'
    return 8 * 600

  @abstractmethod
  def is_needed(self):
    'Return True of the task needs to run.'
    return not brew.has_brew()
  
  #@abstractmethod
  def run(self, options, args):
    'Run the task.'
    brew_options = brew_cli_options()
    brew_options.verbose = options.verbose
    brew_options.password = options.password
    brew_options.blurber = options.blurber
    brew.install(brew_options)
