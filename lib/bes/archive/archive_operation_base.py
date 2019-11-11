#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.common.check import check

class archive_operation_base(with_metaclass(ABCMeta, object)):
  'An archive operation interface.'

  @abstractmethod
  def execute(self, temp_dir):
    'Execute this operation in a temp_dir of the unpacked archive.'
    raise NotImplementedError()

check.register_class(archive_operation_base, name = 'archive_operation')
  
