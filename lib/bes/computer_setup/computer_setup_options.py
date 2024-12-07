#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc
from bes.credentials.credentials import credentials

from .computer_setup_error import computer_setup_error

class _computer_setup_options_desc(bcli_options_desc):

  #@abstractmethod
  def _options_desc(self):
    return '''
verbose  bool  default=False
debug    bool  default=False
dry_run  bool  default=False
password str   secret=True
'''
  
  #@abstractmethod
  def _error_class(self):
    return computer_setup_error
  
class computer_setup_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_computer_setup_options_desc(), **kwargs)

  @property
  def credentials(self):
    return credentials('<cli>', password = self.password)
    
computer_setup_options.register_check_class()
