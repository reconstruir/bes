#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class pipenv_project_cli_args(object):

  def __init__(self):
    pass
  
  def pipenv_project_add_args(self, subparser):

    # pipenv_project_init
    p = subparser.add_parser('init', help = 'Initialize a project.')
    self.__pipenv_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')

    # pipenv_project_install
    p = subparser.add_parser('install', help = 'Install a package.')
    self.__pipenv_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')
    p.add_argument('package_name', action = 'store', type = str, default = None,
                   help = 'The name of the package to install [ None ]')
    p.add_argument('--version', action = 'store', type = str, default = None,
                   help = 'Optional package version.  [ latest ]')

    # pipenv_project_install_requirements
    p = subparser.add_parser('install_requirements', help = 'Install packages from a requirements file.')
    self.__pipenv_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')
    p.add_argument('requirements_file', action = 'store', type = str, default = None,
                   help = 'The requirements file [ None ]')
    
    # pipenv_project_outdated
    p = subparser.add_parser('outdated', help = 'Print outdated packages.')
    self.__pipenv_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')

    # pipenv_project_installed
    p = subparser.add_parser('installed', help = 'Print install packages.')
    self.__pipenv_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')
    
    # pipenv_project_pip
    p = subparser.add_parser('pip', help = 'Run pip command.')
    self.__pipenv_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')
    p.add_argument('args', action = 'store', default = [], nargs = '+',
                   help = 'The pip args. [ None ]')

    # pipenv_project_activate_script
    p = subparser.add_parser('activate_script', help = 'Print the activate script for the virtual env.')
    self.__pipenv_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')
    p.add_argument('--variant', action = 'store', type = str, default = None,
                   help = 'The virtual env variant (csh, fish, ps1) [ None ]')
    
  def __pipenv_project_add_common_args(self, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('-r', '--root-dir', action = 'store', default = None,
                   help = 'The root directory where to install pip [ None ]')
    p.add_argument('-p', '--python-version', action = 'store', default = None,
                   dest = 'python_version',
                   help = 'The python version to use [ None ]')
#    p.add_argument('-c', '--config', action = 'store', default = None,
#                   dest = 'config_filename',
#                   help = 'The config filename to use [ None ]')
     
  def _command_pipenv_project(self, command, *args, **kargs):
    from .pipenv_project_cli_handler import pipenv_project_cli_handler
    return pipenv_project_cli_handler(kargs).handle_command(command)
