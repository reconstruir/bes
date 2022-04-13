#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#

import argparse, os, multiprocessing, pprint, sys, time
from os import path

from collections import namedtuple

from ..system.check import check
from bes.fs.file_path import file_path
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.script.blurb import blurb
from bes.system.env_var import os_env_var
from bes.system.execute import execute
from bes.system.which import which
from bes.system.log import logger

from bes.property.cached_property import cached_property

class dim_task_processor(object):

  _DEFAULT_NUM_PROCESSES = int(((multiprocessing.cpu_count() / 2.0) - 1.0) + 0.5)

  log = logger('processor')
  
  def __init__(self, num_processes = None):
    self._num_processes = num_processes or self._DEFAULT_NUM_PROCESSES

  def run(self, descriptors):
    check.check_dim_task_descriptor_seq(descriptors)

    return self.run_single(descriptors)
    #return self.run_multi(descriptors)
    
  def run_single(self, descriptors):
    check.check_dim_task_descriptor_seq(descriptors)

    build_results = []
    for descriptor in descriptors:
      build_result = descriptor.function(descriptor)
      build_results.append(build_result)
    return build_results

  def run_multi(self, descriptors):
    check.check_dim_task_descriptor_seq(descriptors)
    
    with multiprocessing.Pool(self._num_processes) as pool:
      results = []
      for descriptor in descriptors:
        self.log.log_d('run: adding task {}'.format(descriptor))
        result = pool.apply_async(descriptor.function, args = (descriptor, )) #, callback = task_callback)
        results.append(result)
      self.log.log_d('run: closing pool')
      pool.close()
      self.log.log_d('run: joining')
      pool.join()
      self.log.log_d('run: join returns')

      for i, result in enumerate(results):
        self.log.log_d('run: {}: {}'.format(i, result.get()))
    
    self.log.log_d('run: ends')
    return results
  
#  @classmethod
#  def _task(clazz, i):
#    clazz.log.log_d('task({}) starts'.format(i))
#    time.sleep(1.0)
#    clazz.log.log_d('task({}) ends'.format(i))
#    return 0

