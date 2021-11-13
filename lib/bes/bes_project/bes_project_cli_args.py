#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class bes_project_cli_args(object):

  def __init__(self):
    pass
  
  def bes_project_add_args(self, subparser):

    # create
    p = subparser.add_parser('create', help = 'Create a pip project.')
    self.__bes_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')

    # install
    p = subparser.add_parser('install', help = 'Install a package.')
    self.__bes_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')
    p.add_argument('package_name', action = 'store', type = str, default = None,
                   help = 'The name of the package to install [ None ]')
    p.add_argument('--version', action = 'store', type = str, default = None,
                   help = 'Optional package version.  [ latest ]')

    # upgrade
    p = subparser.add_parser('upgrade', help = 'Upgrade a package.')
    self.__bes_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')
    p.add_argument('packages', action = 'store', default = [], nargs = '+',
                   help = 'The name of the packages to upgrade [ None ]')
    
    # install_requirements
    p = subparser.add_parser('install_requirements', help = 'Install packages from a requirements file.')
    self.__bes_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')
    p.add_argument('requirements_file', action = 'store', type = str, default = None,
                   help = 'The requirements file [ None ]')
    
    # outdated
    p = subparser.add_parser('outdated', help = 'Print outdated packages.')
    self.__bes_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')

    # installed
    p = subparser.add_parser('installed', help = 'Print install packages.')
    self.__bes_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')
    
    # project_pip
    p = subparser.add_parser('pip', help = 'Run pip command.')
    self.__bes_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')
    p.add_argument('args', action = 'store', default = [], nargs = '+',
                   help = 'The pip args. [ None ]')

    # activate_script
    p = subparser.add_parser('activate_script', help = 'Print the activate script for the virtual env.')
    self.__bes_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')
    p.add_argument('--variant', action = 'store', type = str, default = None,
                   help = 'The virtual env variant (csh, fish, ps1) [ None ]')

    # version
    p = subparser.add_parser('version', help = 'Print version of a package.')
    self.__bes_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')
    p.add_argument('package_name', action = 'store', type = str, default = None,
                   help = 'The name of the package to install [ None ]')
    
  def __bes_project_add_common_args(self, p):
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
     
  def _command_bes_project(self, command, *args, **kargs):
    from .bes_project_cli_handler import bes_project_cli_handler
    return bes_project_cli_handler(kargs).handle_command(command)