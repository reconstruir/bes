#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check

from .btask_initializer import btask_initializer

class btask_process_data(namedtuple('btask_process_data', 'name, input_queue, result_queue, nice_level, initializer')):
  
  def __new__(clazz, name, input_queue, result_queue, nice_level = None,
              initializer = None):
    assert input_queue != None
    assert result_queue != None
    check.check_string(name)
    check.check_int(nice_level, allow_none = True)
    initializer = check.check_btask_initializer(initializer, allow_none = True)

    return clazz.__bases__[0].__new__(clazz, name, input_queue, result_queue,
                                      nice_level, initializer)
  
check.register_class(btask_process_data, include_seq = False)
