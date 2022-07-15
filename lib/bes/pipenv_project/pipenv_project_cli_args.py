#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class pipenv_project_cli_args(object):

  def __init__(self):
    pass
  
  def pipenv_project_add_args(self, subparser):

    # create
    p = subparser.add_parser('create', help = 'Create a pipenv project.')
    self.__pipenv_project_add_common_args(p)

    # command
    p = subparser.add_parser('command', help = 'Run an arbitrary pipenv command.')
    self.__pipenv_project_add_common_args(p)
    p.add_argument('args', action = 'store', default = [], nargs = '*',
                   help = 'The command args. [ None ]')

    # install
    p = subparser.add_parser('install', help = 'Install packages.')
    self.__pipenv_project_add_common_args(p)
    p.add_argument('packages', action = 'store', default = [], nargs = '+',
                   help = 'The packages to install [ None ]')
    p.add_argument('--dev', action = 'store_true', default = False,
                   help = 'Install dev packages [ False ]')

    # graph
    p = subparser.add_parser('graph', help = 'Print graph of packages.')
    self.__pipenv_project_add_common_args(p)
    
  def __pipenv_project_add_common_args(self, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('-r', '--root-dir', action = 'store', default = None,
                   help = 'The root directory where to install pip [ None ]')
    p.add_argument('--python-version', action = 'store', default = None,
                   help = 'The python version to use [ None ]')
    p.add_argument('--python-exe', action = 'store', default = None,
                   help = 'The python exe to use [ None ]')
    p.add_argument('--output', action = 'store', default = None,
                   dest = 'output_filename',
                   help = 'Optional output filename [ None ]')
    p.add_argument('--pipfile-dir', action = 'store', default = None,
                   help = 'Directory where to store Pipfile and Pifile.lock [ project_dir ]')
    from bes.data_output.data_output_style import data_output_style
    p.add_argument('--style', action = 'store', default = data_output_style.TABLE,
                   dest = 'output_style',
                   choices = data_output_style.values,
                   help = 'Output style [ TABLE ]')
     
  def _command_pipenv_project(self, command, *args, **kargs):
    from .pipenv_project_cli_handler import pipenv_project_cli_handler
    return pipenv_project_cli_handler(kargs).handle_command(command)
