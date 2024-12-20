#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.system.check import check

class _bf_trash_i(object, metaclass = ABCMeta):

  @classmethod
  @abstractmethod
  def empty_trash(clazz):
    'Empty the trash.'
    raise NotImplementedError('empty_trash')
