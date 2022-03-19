#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class pip_project_cli_args(object):

  def __init__(self):
    pass
  
  def pip_project_add_args(self, subparser):

    # create
    p = subparser.add_parser('create', help = 'Create a pip project.')
    self.__pip_project_add_common_args(p)

    # install
    p = subparser.add_parser('install', help = 'Install a package.')
    self.__pip_project_add_common_args(p)
    p.add_argument('package_name', action = 'store', type = str, default = None,
                   help = 'The name of the package to install [ None ]')
    p.add_argument('--version', action = 'store', type = str, default = None,
                   help = 'Optional package version.  [ latest ]')

    # upgrade
    p = subparser.add_parser('upgrade', help = 'Upgrade a package.')
    self.__pip_project_add_common_args(p)
    p.add_argument('packages', action = 'store', default = [], nargs = '+',
                   help = 'The name of the packages to upgrade [ None ]')
    
    # install_requirements
    p = subparser.add_parser('install_requirements', help = 'Install packages from a requirements file.')
    self.__pip_project_add_common_args(p)
    p.add_argument('requirements_files', action = 'store', default = [], nargs = '+',
                   help = 'One or more requirements files [ None ]')
    
    # outdated
    p = subparser.add_parser('outdated', help = 'Print outdated packages.')
    self.__pip_project_add_common_args(p)

    # installed
    p = subparser.add_parser('installed', help = 'Print install packages.')
    self.__pip_project_add_common_args(p)
    
    # project_pip
    p = subparser.add_parser('pip', help = 'Run pip command.')
    self.__pip_project_add_common_args(p)
    p.add_argument('args', action = 'store', default = [], nargs = '+',
                   help = 'The pip args. [ None ]')

    # activate_script
    p = subparser.add_parser('activate_script', help = 'Print the activate script for the virtual env.')
    self.__pip_project_add_common_args(p)
    p.add_argument('--variant', action = 'store', type = str, default = None,
                   help = 'The virtual env variant (csh, fish, ps1) [ None ]')
#    p.add_argument('--write-activate-script', action = 'store', default = None,
#                   help = 'Write the activate script to the given file [ None ]')

    # version
    p = subparser.add_parser('version', help = 'Print version of a package.')
    self.__pip_project_add_common_args(p)
    p.add_argument('package_name', action = 'store', type = str, default = None,
                   help = 'The name of the package to install [ None ]')
    
  def __pip_project_add_common_args(self, p):
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
    from bes.data_output.data_output_style import data_output_style
    p.add_argument('--style', action = 'store', default = data_output_style.TABLE,
                   dest = 'output_style',
                   choices = data_output_style.values,
                   help = 'Output style [ TABLE ]')
     
  def _command_pip_project(self, command, *args, **kargs):
    from .pip_project_cli_handler import pip_project_cli_handler
    return pip_project_cli_handler(kargs).handle_command(command)
