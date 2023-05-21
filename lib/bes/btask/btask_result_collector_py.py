#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.log import logger
from bes.system.check import check

from .btask_result_collector_i import btask_result_collector_i
from .btask_result import btask_result
from .btask_pool import btask_pool

class btask_result_collector_py(btask_result_collector_i):

  _log = logger('btask')
  
  def __init__(self, pool, runner):
    check.check_btask_pool(pool)
    check.check_btask_main_thread_runner(runner)
    
    super().__init__(pool.result_queue)
    
    self._pool = pool
    self._runner = runner
  
  #@abstractmethod
  def handle_result(self, result):
    check.check_btask_result(result)

    self._log.log_d(f'btask_result_collector_py.handle_result: task_id={result.task_id}')
    self._runner.call_in_main_thread(self._handle_result_in_main_thread, result)

  #@abstractmethod
  def handle_progress(self, progress):
    check.check_btask_progress(progress)

    self._log.log_d(f'btask_result_collector_py.handle_progress: task_id={progress.task_id}')
    self._runner.call_in_main_thread(self._handle_progress_in_main_thread, progress)
    
  def _handle_result_in_main_thread(self, result):
    check.check_btask_result(result)
    self._log.log_d(f'btask_result_collector_py._handle_result_in_main_thread: task_id={result.task_id}')
    callback = self._pool.complete(result.task_id)
    callback(result)

  def _handle_progress_in_main_thread(self, progress):
    check.check_btask_progress(progress)
    self._log.log_d(f'btask_result_collector_py._handle_progress_in_main_thread: task_id={progress.task_id}')
    self._pool.report_progress(task_id, progress)
    
