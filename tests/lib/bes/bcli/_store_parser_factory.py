#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_factory_i import bcli_command_factory_i

class _store_parser_factory(bcli_command_factory_i):

  @classmethod
  #@abstractmethod
  def path(clazz):
    return 'store'

  #@abstractmethod
  def error_class(self):
    raise RuntimeError

  #@abstractmethod
  def options_class(self):
    return None
  
  #@abstractmethod
  def has_commands(self):
    return True

  #@abstractmethod
  def add_commands(self, subparsers):
    p = subparsers.add_parser('buy', help = 'Buy something.')
    p.add_argument('what', action = 'store', type = str,
                   help = 'What to buy')

    p = subparsers.add_parser('sell', help = 'Sell something.')
    p.add_argument('what', action = 'store', type = str,
                   help = 'What to sell')
    
  #@abstractmethod
  def add_arguments(self, parser):
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False,
                        help = 'Verbose [ False ]')

  #@abstractmethod
  def handler_class(self):
    from _store_command_handler import _store_command_handler
    return _store_command_handler
    
