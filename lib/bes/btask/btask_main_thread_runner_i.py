#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.system.check import check

class btask_main_thread_runner_i(object, metaclass = ABCMeta):

  @abstractmethod
  def call_in_main_thread(self, function, *args, **kwargs):
    raise NotImplementedError('call_in_main_thread')

check.register_class(btask_main_thread_runner_i, name = 'btask_main_thread_runner', include_seq = False)
