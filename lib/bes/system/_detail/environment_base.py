#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class environment_base(with_metaclass(ABCMeta, object)):
  'Abstract interface for dealing with system specific non portable environment stuff.'

  @classmethod
  @abstractmethod
  def home_dir_env(clazz, home_dir):
    'Return a dict with the environment needed to set the home directory.'
    raise NotImplemented('home_dir_env')
  
