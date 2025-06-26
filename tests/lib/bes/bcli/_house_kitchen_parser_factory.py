#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_parser_factory_i import bcli_parser_factory_i

class _house_kitchen_parser_factory(bcli_parser_factory_i):

  @classmethod
  #@abstractmethod
  def path(clazz):
    return 'house/kitchen'

  #@abstractmethod
  def error_class(self):
    raise RuntimeError

  #@abstractmethod
  def options_class(self):
    return None
  
  #@abstractmethod
  def has_sub_parsers(self):
    return True

  #@abstractmethod
  def add_sub_parsers(self, subparsers):
    p = subparsers.add_parser('cook', help = 'Cook some food.')
    p.add_argument('what', action = 'store', type = str,
                   help = 'What to cook')
    p.add_argument('--method', action = 'store', type = str, default = 'sear',
                   choices = ( 'sear', 'steam', 'grill' ),
                   help = 'Cooking method [ sear ]')
    
    p = subparsers.add_parser('clean', help = 'Clean the kitchen.')
   
  #@abstractmethod
  def add_arguments(self, parser):
    parser.add_argument('--output', action = 'store', type = str, default = 'json',
                        choices = ( 'json', 'text' ),
                        help = 'Output style [ json ]')
