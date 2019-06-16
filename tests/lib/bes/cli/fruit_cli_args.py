#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class fruit_cli_args(object):

  def __init__(self):
    pass
  
  def fruit_add_args(self, subparser):
    # fruit_order
    p = subparser.add_parser('order', help = 'Order some fruit.')
    p.add_argument('fruit_type', action = 'store', default = 'apple', type = str,
                   choices = [ 'apple', 'kiwi', 'lemon' ],
                   help = 'Type of fruit to order. [ None ]')
    p.add_argument('num', action = 'store', default = 1, type = int,
                   help = 'Number of pieces of fruit to order. [ 1 ]')
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dry run. [ False ]')

    p = subparser.add_parser('make_pie', help = 'Make a fruit pie.')
    p.add_argument('fruits', action = 'store', default = None, type = str, nargs = '+',
                   help = 'Make a fruit pie. [ None ]')
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dry run. [ False ]')

    p = subparser.add_parser('fail', help = 'Forced failure.')
    
  def _command_fruit_order(self, fruit_type, num, dry_run):
    print('_command_fruit_order(fruit_type={}, num={}, dry_run={})'.format(fruit_type, num, dry_run))
    return 0

  def _command_fruit_make_pie(self, fruits, dry_run):
    print('_command_fruit_make_pie(fruits={}, dry_run={})'.format(fruits, dry_run))
    return 0

  def _command_fruit_fail(self):
    print('_command_fruit_fail()')
    return 1
  
