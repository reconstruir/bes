#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class shell_framework_cli_args(object):

  def __init__(self):
    pass

  def shell_framework_add_args(self, subparser):

    # update
    p = subparser.add_parser('update', help = 'Update the framework.')
    self.__shell_framework_add_common_args(p)

    # latest
    p = subparser.add_parser('latest', help = 'Print the latest git revision available.')
    self.__shell_framework_add_common_args(p)

  def __shell_framework_add_common_args(self, p):
    from .shell_framework_defaults import shell_framework_defaults
    
    p.add_argument('-d', '--dest-dir', action = 'store', default = shell_framework_defaults.DEST_DIR,
                   help = 'Directory where to update the framework to [ {} ]'.format(shell_framework_defaults.DEST_DIR))
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('--debug', action = 'store_true', default = False,
                   help = 'Debug mode [ False ]')
    p.add_argument('--address', action = 'store', default = shell_framework_defaults.ADDRESS,
                   help = 'The bes_shell git repo address [ {} ]'.format(shell_framework_defaults.ADDRESS))
    p.add_argument('--framework-basename', action = 'store', default = shell_framework_defaults.FRAMEWORK_BASENAME,
                   help = 'The framework directory basename [ {} ]'.format(shell_framework_defaults.FRAMEWORK_BASENAME))
    p.add_argument('--revision-basename', action = 'store', default = shell_framework_defaults.REVISION_BASENAME,
                   help = 'The revision filename basename [ {} ]'.format(shell_framework_defaults.REVISION_BASENAME))
    p.add_argument('-r', '--revision', action = 'store', default = shell_framework_defaults.REVISION,
                   help = 'The git revision [ {} ]'.format(shell_framework_defaults.REVISION))
    
  def _command_shell_framework(self, command, *args, **kargs):
    from .shell_framework_cli_handler import shell_framework_cli_handler
    return shell_framework_cli_handler(kargs).handle_command(command)
