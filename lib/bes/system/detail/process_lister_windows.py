#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .process_lister_base import process_lister_base

from bes.system.execute import execute

class process_lister_windows(platform_determiner_base):

  #@abstractmethod
  def list_processes(self):
    'List all processes.'
    raise NotImplemented('list_processes')
