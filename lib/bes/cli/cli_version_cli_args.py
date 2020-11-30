# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.version.version_cli import version_cli

class cli_version_cli_args(object):

  def version_add_args(self, parser):
    version_cli.arg_sub_parser_add_arguments(parser)
  
  def _command_version(self, command, *args, **kargs):
    assert command == None
    assert 'print_all' in kargs
    assert 'brief' in kargs
    version_cli.print_everything(self.version_module_name,
                                 dependencies = self.version_dependencies,
                                 brief = kargs['brief'],
                                 print_all = kargs['print_all'])
    return 0
