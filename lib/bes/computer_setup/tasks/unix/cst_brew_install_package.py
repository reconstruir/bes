#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from bes.computer_setup.computer_setup_task import computer_setup_task

from bes.unix.brew.brew import brew

class cst_brew_install_package(computer_setup_task):

  #@abstractmethod
  def name(self):
    'Name for task.'
    return 'brew_install_package'

  #@abstractmethod
  def description(self):
    'Description for task.'
    return 'Install brew packages'

  #@abstractmethod
  def average_duration(self):
    'Average duration in seconds.'
    return 0

  @abstractmethod
  def is_needed(self):
    'Return True of the task needs to run.'
    return not brew.has_package('foo')
  
  #@abstractmethod
  def run(self, options, args):
    'Run the task.'
    brew.install_package('foo')
