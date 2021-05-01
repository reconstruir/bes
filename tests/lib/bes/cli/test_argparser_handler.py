#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import sys

from bes.system.host import host
from bes.testing.program_unit_test import program_unit_test
from bes.fs.file_util import file_util

class test_argparser_handler(program_unit_test):

  def test_fruit_order(self):
    program = self._make_test_program()
    rv = self.run_program(program, [ 'fruit', 'order', 'kiwi', '10' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( '_command_fruit_order(fruit_type=kiwi, num=10, dry_run=False)', rv.output )
    
  def test_fruit_fail(self):
    program = self._make_test_program()
    rv = self.run_program(program, [ 'fruit', 'fail' ])
    self.assertEqual( 1, rv.exit_code )
    self.assertEqual( '_command_fruit_fail()', rv.output )

  def test_cheese_churn(self):
    program = self._make_test_program()
    rv = self.run_program(program, [ 'cheese', 'churn', '20' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( '_command_cheese_churn(duration=20, dry_run=False)', rv.output )
    
  def test_cheese_fail(self):
    program = self._make_test_program()
    rv = self.run_program(program, [ 'cheese', 'fail' ])
    self.assertEqual( 1, rv.exit_code )
    self.assertEqual( '_command_cheese_fail()', rv.output )
    
  def test_version(self):
    program = self._make_test_program()
    rv = self.run_program(program, [ 'version', '--brief' ])
    self.assertEqual( 0, rv.exit_code )

    rv = self.run_program(program, [ 'version', '--all' ])
    self.assertEqual( 0, rv.exit_code )

  def _make_test_program(self):
    tmp_dir = self.make_temp_dir()
    file_util.save(path.join(tmp_dir, 'farm_cli.py'), content = self._FARM_CLI_DOT_PY )
    file_util.save(path.join(tmp_dir, 'fruit_cli_args.py'), content = self._FRUIT_CLI_ARGS_DOT_PY )
    file_util.save(path.join(tmp_dir, 'cheese_cli_args.py'), content = self._CHEESE_CLI_ARGS_DOT_PY )
    unix_program = file_util.save(path.join(tmp_dir, 'farm.py'), content = self._FARM_DOT_PY)
    if host.is_unix():
      program = unix_program
    elif host.is_windows():
      content = self._FARM_DOT_BAT.format(executable = sys.executable)
      program = file_util.save(path.join(tmp_dir, 'farm.bat'), content = content)
    else:
      host.raise_unsupported_system()
    return program

  _FARM_DOT_PY = '''\
#!/usr/bin/env python

from farm_cli import farm_cli

__author__ = 'chupacabra@example.com'
__bes_address__ = 'https://www.example.com/'
__bes_author_name__ = 'Chupacabra'
__bes_tag__ = 'master'
__bes_timestamp__ = 'yesterday'
__version__ = '6.6.6'

if __name__ == '__main__':
  farm_cli.run()
'''

  _FARM_DOT_BAT = '''\
@echo off
"{executable}" %~dp0/farm.py %*
'''

  _FARM_CLI_DOT_PY = '''\
from bes.cli.cli import cli
from bes.cli.cli_command import cli_command

class farm_cli(cli):

  def __init__(self):
    super(farm_cli, self).__init__('farm')
    
  #@abstractmethod
  def command_group_list(self):
    'Return a list of command groups for this cli.'
    from fruit_cli_args import fruit_cli_args
    from cheese_cli_args import cheese_cli_args
    return [
      cli_command('fruit', 'fruit_add_args', 'Deal with fruit', fruit_cli_args),
      cli_command('cheese', 'cheese_add_args', 'Deal with cheese', cheese_cli_args),
    ]

  #@abstractmethod
  def command_list(self):
    'Return a list of commands for this cli.'
    from bes.cli.cli_env_cli_args import cli_env_cli_args
    from bes.cli.cli_version_cli_args import cli_version_cli_args
    from bes.cli.cli_help_cli_args import cli_help_cli_args
    cli_version_cli_args.version_module_name = 'bes'
    cli_version_cli_args.version_dependencies = None
    return [
      cli_command('env', 'env_add_args', 'Print env information', cli_env_cli_args),
      cli_command('help', 'help_add_args', 'Print help', cli_help_cli_args),
      cli_command('version', 'version_add_args', 'Print version information', cli_version_cli_args),
    ]
  
  @classmethod
  def run(clazz):
    raise SystemExit(farm_cli().main())
'''

  _FRUIT_CLI_ARGS_DOT_PY = '''\
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
'''

  _CHEESE_CLI_ARGS_DOT_PY = '''
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
'''  

if __name__ == '__main__':
  program_unit_test.main()
