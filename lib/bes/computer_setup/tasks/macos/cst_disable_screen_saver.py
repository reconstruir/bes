#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from bes.computer_setup.computer_setup_task import computer_setup_task
from bes.macos.defaults.defaults import defaults

class cst_disable_screen_saver(computer_setup_task):

  def __init__(self, *args, **kargs):
    super(cst_disable_screen_saver, self).__init__(*args, **kargs)

  #@abstractmethod
  def name(self):
    'Name for task.'
    return 'disable_screen_saver'

  #@abstractmethod
  def description(self):
    'Description for task.'
    return 'Disable the screensaver'

  #@abstractmethod
  def average_duration(self):
    'Average duration in seconds.'
    return 0

  @abstractmethod
  def is_needed(self):
    'Return True of the task needs to run.'
    value = defaults.get_value('com.apple.screensaver', 'idleTime')
    return value != '0'
  
  #@abstractmethod
  def run(self):
    'Run the task.'
    defaults.set_value('com.apple.screensaver', 'idleTime', 0)
