#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from bes.computer_setup.computer_setup_task import computer_setup_task
from bes.macos.scutil.scutil import scutil

class cst_change_computer_name(computer_setup_task):

  #@abstractmethod
  def name(self):
    'Name for task.'
    return 'change_computer_name'

  #@abstractmethod
  def description(self):
    'Description for task.'
    return 'Change the computer name'

  #@abstractmethod
  def average_duration(self):
    'Average duration in seconds.'
    return 0

  #@abstractmethod
  def is_needed(self):
    'Return True of the task needs to run.'

    computer_name = 'caca1'
    
    ComputerName = scutil.get_value('ComputerName')
    LocalHostName = scutil.get_value('LocalHostName')
    HostName = scutil.get_value('HostName')
    return ComputerName != computer_name or LocalHostName != computer_name or HostName or computer_name    
  
  #@abstractmethod
  def run(self, options):
    'Run the task.'

    computer_name = 'caca1'
    print(self.values)

    print(scutil.get_value('ComputerName'))
    print(scutil.get_value('LocalHostName'))
    print(scutil.get_value('HostName'))

    #scutil.set_value('ComputerName', computer_name)
    #scutil.set_value('LocalHostName', computer_name)
    #scutil.set_value('HostName', computer_name)
    
