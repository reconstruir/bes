#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.log import logger
from bes.system.check import check

from .btask_error import btask_error
from .btask_pool_item import btask_pool_item

class btask_pool_queue(object):

  _log = logger('btask')

  def __init__(self):
    self._tasks = {}

  def add(self, item):
    check.check_btask_pool_item(item)

    category = item.config.category
    self._ensure_category(category)
    item_list = self._tasks[category]
    item_list.append(item)
    item_list.sort(key = lambda item: ( item.config.priority, item.add_time ))

  def category_count(self, category):
    check.check_string(category)

    self._ensure_category(category)
    return len(self._tasks[category])
    
  def remove_by_category(self, category):
    check.check_string(category)

    for next_category, item_list in self._tasks.items():
      if next_category == category:
        if not item_list:
          return None
        item = item_list.pop(0)
        return item
    return None

  def remove_by_task_id(self, task_id):
    check.check_int(task_id)

    for next_category, item_list in self._tasks.items():
      for i, next_item in enumerate(item_list):
        if next_item.task_id == task_id:
          popped_item = item_list.pop(i)
          assert id(popped_item) == id(next_item)
          return next_item
    return None

  def find_by_task_id(self, task_id):
    check.check_int(task_id)

    for next_category, item_list in self._tasks.items():
      for i, next_item in enumerate(item_list):
        if next_item.task_id == task_id:
          return next_item
    return None
  
  def _ensure_category(self, category):
    if category in self._tasks:
      return
    self._tasks[category] = []
    
check.register_class(btask_pool_queue, include_seq = False)
