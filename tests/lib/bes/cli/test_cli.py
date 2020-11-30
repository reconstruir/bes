#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.testing.program_unit_test import program_unit_test
from bes.fs.file_util import file_util
from bes.system.host import host

class test_cli(program_unit_test):

#  if host.is_unix():
#    _program = program_unit_test.file_path(__file__, 'fake_program.py')
#  elif host.is_windows():
#    _program = program_unit_test.file_path(__file__, 'fake_program.bat')
#  else:
#    host.raise_unsupported_system()
  
  def test_caca(self):

    kitchen_program_content = '''\
#!/usr/bin/env python
from kitchen_cli import kitchen_cli

if __name__ == '__main__':
  kitchen_cli.run()
'''

    knife_cli_args_content = '''\
class knife_cli_args(object):

  def knife_add_args(self, subparser):
    p = subparser.add_parser('cut', help = 'Cut something.')
    p.add_argument('what', action = 'store', default = None, help = 'What to cut []')

  def _command_knife(self, command, *args, **kargs):
    func = getattr(self, command)
    return func(*args, **kargs)

  @classmethod
  def cut(clazz, what):
    print('cut({})'.format(what))
    return 0
'''

    oven_cli_args_content = '''\
class oven_cli_args(object):

  def oven_add_args(self, subparser):
    p = subparser.add_parser('bake', help = 'Bake something.')
    p.add_argument('what', action = 'store', default = None, help = 'What to bake []')

  def _command_oven(self, command, *args, **kargs):
    func = getattr(self, command)
    return func(*args, **kargs)

  @classmethod
  def bake(clazz, what):
    print('bake({})'.format(what))
    return 0
'''
    
    kitchen_cli_content = '''\
from bes.cli.cli_item import cli_item
from bes.cli.cli import cli

from knife_cli_args import knife_cli_args
from oven_cli_args import oven_cli_args

class kitchen_cli(cli):

  def __init__(self):
    super(kitchen_cli, self).__init__('kitchen')

  #@abstractmethod
  def tool_item_list(self):
    'Return a list of tool items for this cli.'
    return [
      cli_item('knife', 'knife_add_args', 'Knife', knife_cli_args),
      cli_item('oven', 'oven_add_args', 'Oven', oven_cli_args),
    ]

  @classmethod
  def run(clazz):
    raise SystemExit(kitchen_cli().main())
'''
    
    tmp = self.make_temp_dir()
    kitchen_program = file_util.save(path.join(tmp, 'kitchen.py'), content = kitchen_program_content)
    file_util.save(path.join(tmp, 'knife_cli_args.py'), content = knife_cli_args_content)
    file_util.save(path.join(tmp, 'oven_cli_args.py'), content = oven_cli_args_content)
    file_util.save(path.join(tmp, 'kitchen_cli.py'), content = kitchen_cli_content)

    rv = self.run_program(kitchen_program, [ 'knife', 'cut', 'bread' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'cut(bread)', rv.output.strip() )

    rv = self.run_program(kitchen_program, [ 'oven', 'bake', 'cheesecake' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'bake(cheesecake)', rv.output.strip() )
    
if __name__ == '__main__':
  program_unit_test.main()
