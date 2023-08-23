#!/usr/bin/env python3

from collections import namedtuple
from datetime import datetime

import pickle
import multiprocessing
import time

from bes.system.log import logger
from bes.system.check import check
from bes.common.tuple_util import tuple_util

from bes.bprocess.bprocess_pool_item import bprocess_pool_item

class btask_data(namedtuple('btask_data', 'initializer, initializer_args, input_queue, output_queue')):
  
  def __new__(clazz, initializer, initializer_args, input_queue, output_queue):
    check.check_callable(initializer, allow_none = True)
    check.check_tuple(initializer_args, allow_none = True)

    return clazz.__bases__[0].__new__(clazz, initializer, initializer_args, input_queue, output_queue)

  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
check.register_class(btask_data, include_seq = False, cast_func = btask_data._check_cast_func)

_log = logger('kiwi')

def _function(context, args):
  clazz._log.log_d(f'_function: task_id={context.task_id} args={args}')

def _process(encoded_task_data):
  check.check_bytes(encoded_task_data)

  decoded_task_data = pickle.loads(encoded_task_data)
  _log.log_d(f'decoded_task_data={decoded_task_data}')
  if decoded_task_data.initializer:
    args = decoded_task_data.initializer_args or ()
    decoded_task_data.initializer(*args)

  time.sleep(5)
  return 0

def _init(size, version):
  _log.log_d(f'_init: size={size} version={version}')
  
def main():
  _log.log_d(f'main()')
  manager = multiprocessing.Manager()
  input_queue = manager.Queue()
  output_queue = manager.Queue()
  task_data = btask_data(_init, ( 'large', 10.2 ), input_queue, output_queue)
  data = {
    'color': 'green',
    'flavor': 'tart',
    'price': 6.66,
    'init': _init,
    'init_args': ( 'large', 10.2 ),
    'input_queue': input_queue,
    'output_queue': output_queue,
  }

  item = bprocess_pool_item(1, datetime.now(), None, function, args, callback, progress_callback, cancelled)
  
  encoded_task_data = pickle.dumps(task_data)
  p = multiprocessing.Process (name = 'ppp',
                              target = _process,
                              args = ( encoded_task_data, ))
  p.start()
  p.join()
  exit_code = p.exitcode
  _log.log_d(f'exit_code={exit_code}')
  return 0

if __name__ == '__main__':
  raise SystemExit(main())
