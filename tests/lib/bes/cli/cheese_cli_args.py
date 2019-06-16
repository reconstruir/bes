#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class cheese_cli_args(object):

  def __init__(self):
    pass
  
  def cheese_add_args(self, subparser):
    # cheese_churn
    p = subparser.add_parser('churn', help = 'Churn some cheese.')
    p.add_argument('duration', action = 'store', default = 10, type = int,
                   help = 'Minutes to churn the cheese for. [ 10 ]')
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dry run. [ False ]')

    p = subparser.add_parser('deliver', help = 'Deliver cheese to the grocery.')
    p.add_argument('cheese_type', action = 'store', default = 'gouda', type = str,
                   choices = [ 'gouda', 'brie', 'parrano' ],
                   help = 'The cheese type to deliver. [ None ]')
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dry run. [ False ]')
    
    p = subparser.add_parser('fail', help = 'Forced failure.')
    
  def _command_cheese_churn(self, duration, dry_run):
    print('_command_cheese_churn(duration={}, dry_run={})'.format(duration, dry_run))
    return 0

  def _command_cheese_deliver(self, cheeses, dry_run):
    print('_command_cheese_deliver(cheeses={}, dry_run={})'.format(cheeses, dry_run))
    return 0

  def _command_cheese_fail(self):
    print('_command_cheese_fail()')
    return 1
  
