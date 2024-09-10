#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from ..system.check import check

class git_operation_base(object, metaclass = ABCMeta):
  'Abstract interface for git operations.'
  
  @abstractmethod
  def run(self, repo):
    'Return True if vmware is installed.'
    raise NotImplemented('run')

check.register_class(git_operation_base, name = 'git_operation', include_seq = True)
