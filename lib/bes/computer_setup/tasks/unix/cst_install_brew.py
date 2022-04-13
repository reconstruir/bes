#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from bes.computer_setup.computer_setup_task import computer_setup_task

from bes.unix.brew_installer.brew_installer import brew_installer
from bes.unix.brew_installer.brew_installer_options import brew_installer_options

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

  #@abstractmethod
  def is_needed(self):
    'Return True of the task needs to run.'
    return not brew.is_installed()
  
  #@abstractmethod
  def run(self, options, args):
    'Run the task.'
    brew_options = brew_installer_options()
    brew_options.verbose = options.verbose
    brew_options.password = options.password
    brew_options.blurber = options.blurber
    brew_installer.install(brew_options)
