#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check

class btask_process_data(namedtuple('btask_process_data', 'name, initializer, initializer_args, input_queue, output_queue, nice_level')):
  
  def __new__(clazz, input_queue, output_queue,
              name = None, nice_level = None,
              initializer = None, initializer_args = None):
    assert input_queue != None
    assert output_queue != None
    check.check_string(name, allow_none = True)
    check.check_int(nice_level, allow_none = True)
    check.check_callable(initializer, allow_none = True)
    check.check_tuple(initializer_args, allow_none = True)

    return clazz.__bases__[0].__new__(clazz, input_queue, output_queue,
                                      name, nice_level,
                                      initializer, initializer_args)
  
check.register_class(btask_process_data, include_seq = False)