#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class process_lister_base(with_metaclass(ABCMeta, object)):
  'Abstract interface for listing processes.'
  
  @abstractmethod
  def list_processes(self):
    'List all processes.'
    raise NotImplemented('list_processes')
