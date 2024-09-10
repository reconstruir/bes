#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

class process_lister_base(object, metaclass = ABCMeta):
  'Abstract interface for listing processes.'

  @classmethod
  @abstractmethod
  def list_processes(clazz):
    'List all processes.'
    raise NotImplemented('list_processes')

  @classmethod
  @abstractmethod
  def open_files(clazz, pid):
    'Return a list of open files for pid or None if pid not found.'
    raise NotImplemented('open_files')
