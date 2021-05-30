#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class pyinstaller_cli_args(object):

  def __init__(self):
    pass
  
  def pyinstaller_add_args(self, subparser):

    # build
    p = subparser.add_parser('build', help = 'Build a pyinstaller executable.')
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('-d', '--debug', action = 'store_true', default = False,
                   help = 'Debug mode [ False ]')
    p.add_argument('--build-dir', action = 'store', default = 'BUILD',
                   help = 'Build dir [ False ]')
    p.add_argument('--clean', action = 'store_true', default = False,
                   help = 'Clean first [ False ]')
    p.add_argument('--exclude', action = 'append', default = [],
                   dest = 'excludes',
                   help = 'Exclude the given python module []')
    p.add_argument('--hidden-import', action = 'append', default = [],
                   dest = 'hidden_imports',
                   help = 'Force include the given hidden import []')
    p.add_argument('--log-level', action = 'store', default = 'INFO',
                   help = 'PyInstaller log level [ INFO ]')
    p.add_argument('--python-version', action = 'store', default = '3.8',
                   help = 'The python version to use. [ 3.8 ]')
    p.add_argument('script_filename', action = 'store', default = None,
                   help = 'The python script []')
    p.add_argument('output_filename', action = 'store', default = None,
                   help = 'The output exe filename []')
    
  def _command_pyinstaller(self, command, *args, **kargs):
    from .pyinstaller_cli_handler import pyinstaller_cli_handler
    return pyinstaller_cli_handler(kargs).handle_command(command)
