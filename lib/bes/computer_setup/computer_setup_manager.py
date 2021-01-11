#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.config.simple_config import simple_config

from .computer_setup_options import computer_setup_options

class computer_setup_manager(object):
  
  def __init__(self, options = None):
    self._options = options or computer_setup_options()
    self._tasks = []

  def run(self):
    num_tasks = len(self._tasks)
    for i, task in enumerate(self._tasks, start = 1):
      needed = task.is_needed()
      needed_blurb = '- not needed' if not needed else ''
      print('{} of {}: {} {}'.format(i, num_tasks, task.name(), needed_blurb))
      if needed:
        if self.options.dry_run:
          print('DRY_RUN: would run: {}'.format(task.name()))
        else:
          task.run()

  def add_task(self, task):
    check.check_computer_setup_task(task)

    self._tasks.append(task)

  def add_tasks_from_config(self, config_filename):
    check.check_string(config_filename)

    config = simple_config.from_file(config_filename)
    for section in config:
      print('caca: {}'.format(section.header_))
    
check.register_class(computer_setup_manager)
