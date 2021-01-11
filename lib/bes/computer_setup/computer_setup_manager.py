#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.config.simple_config import simple_config
from bes.key_value.key_value_list import key_value_list
from bes.system.host import host
from bes.system.log import logger

from .computer_setup_options import computer_setup_options
from .computer_setup_error import computer_setup_error
from .computer_setup_task_registry import computer_setup_task_registry

class computer_setup_manager(object):

  _log = logger('vmware_client')
  
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
    self._log.log_i('add_task({})'.format(str(task)))

    self._tasks.append(task)

  def add_tasks_from_config(self, config_filename):
    check.check_string(config_filename)

    config = simple_config.from_file(config_filename)
    for section in config:
      task = self._parse_task(section)
      if task:
        self.add_task(task)

  def _parse_task(self, section):
    check.check_simple_config_section(section)

    values = section.to_dict(resolve_env_vars = True)

    system = values.pop('system', None)
    if system and system != host.SYSTEM:
      self._log.log_d('system {} does not match us {}'.format(system, host.SYSTEM))
      return None
    task_class_name = values.pop('class', None)
    if not task_class_name:
      raise computer_setup_error('class missing for task "{}" - {}'.format(section.header_.name,
                                                                           section.header_.origin))
    task_class = computer_setup_task_registry.get(task_class_name)
    if not task_class:
      origin = section.get_value_origin('class')
      raise computer_setup_error('unknown task class "{}" - {}'.format(task_class_name,
                                                                       origin,
                                                                       section.header_.origin))
      
    task_values = key_value_list()
    #print('task_class={}'.format(task_class))
    for next_values in section.get_all_values('value'):
      task_values.extend(key_value_list.parse(next_values))
    task = task_class()
    task.values = task_values
    return task
      
check.register_class(computer_setup_manager)
