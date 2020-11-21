#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.common.check import check
from bes.script.blurber import blurber
from bes.system.compat import with_metaclass

from .computer_setup_task_options import computer_setup_task_options

class computer_setup_task_base(with_metaclass(ABCMeta, object)):

  def __init__(self, options = None):
    options = options or computer_setup_task_options()
    check.check_computer_setup_task_options(options)
    self.options = options

  @abstractmethod
  def name(self):
    'Name for task.'
    raise NotImplemented('name')

  @abstractmethod
  def description(self):
    'Description for task.'
    raise NotImplemented('description')

  @abstractmethod
  def average_duration(self):
    'Average duration in seconds.'
    raise NotImplemented('average_duration')

  @abstractmethod
  def is_needed(self):
    'Return True of the task needs to run.'
    raise NotImplemented('run')

  @abstractmethod
  def run(self, verbose):
    'Run the task.'
    raise NotImplemented('run')

  @property
  def blurber(self):
    return self.options.blurber
  
  def blurb(self, message, output = None, fit = False):
    self.blurber.blurb(message, output = output, fit = fit)
    
  def blurb_verbose(self, message, output = None, fit = False):
    self.blurber.blurb_verbose(message, output = output, fit = fit)
