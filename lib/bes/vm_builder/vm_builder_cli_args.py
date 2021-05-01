#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class vm_builder_cli_args(object):
  'Commands for manipulating vm builder vms'

  def __init__(self):
    pass
  
  def vm_builder_add_args(self, subparser):

    # vm_builder_ssh_setup
    p = subparser.add_parser('vm_builder_ssh_setup', help = 'Setup ssh config inside a vm builder instance.')
    self.__vm_builder_add_common_args(p)
    p.add_argument('ssh_config_dir', action = 'store', default = None, type = str,
                   help = 'The ssh config dir. [ None ]')
    p.add_argument('username', default = None, type = str,
                   help = 'The username to use in the ssh config file.')
    p.add_argument('ssh_public_key', default = None, type = str,
                   help = 'The ssh public key for accessing a remote git repo.')
    p.add_argument('ssh_private_key', default = None, type = str,
                   help = 'The ssh private key for accessing a remote git repo.')
    p.add_argument('domain_name', default = None, type = str,
                   help = 'The domain name of the remote git repo.')
    p.add_argument('builder_access_ssh_public_key', default = None, type = str,
                   help = 'The ssh public key for accessing the builder.')

    # vm_host_ssh_setup
    p = subparser.add_parser('vm_host_ssh_setup', help = 'Setup ssh config inside a vm host instance.')
    self.__vm_builder_add_common_args(p)
    p.add_argument('ssh_config_dir', action = 'store', default = None, type = str,
                   help = 'The ssh config dir. [ None ]')
    p.add_argument('filename', action = 'store', default = None, type = str,
                   help = 'The filename for the ssh key. [ None ]')
    p.add_argument('username', default = 'vagrant',
                   help = 'The username to use in the ssh config file.')
    p.add_argument('builder_access_ssh_public_key', default = None, type = str,
                   help = 'The ssh public key for accessing the builder.')
    p.add_argument('builder_access_ssh_private_key', default = None, type = str,
                   help = 'The ssh private key for accessing the builder.')

  def __vm_builder_add_common_args(self, p):
    p.add_argument('--dont-include-ip-address', action = 'store_true', default = False,
                   help = 'Whether to include the ip address in known_hosts.')
    p.add_argument('--dont-include-comment', action = 'store_true', default = False,
                   help = 'Whether to include the comment in the known_hosts.')

  def _command_vm_builder(self, command, *args, **kargs):
    from .vm_builder_cli_handler import vm_builder_cli_handler
    return vm_builder_cli_handler(kargs).handle_command(command)
