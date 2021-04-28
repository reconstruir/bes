#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.cli.cli_command_handler import cli_command_handler
from bes.system.log import logger
from bes.fs.file_util import file_util

from bes.ssh_config.ssh_config_manager import ssh_config_manager

from .vm_builder_cli_options import vm_builder_cli_options

class vm_builder_cli_handler(cli_command_handler):

  log = logger('vm_builder')

  def __init__(self, cli_args):
    super(vm_builder_cli_handler, self).__init__(cli_args, options_class = vm_builder_cli_options)
    check.check_vm_builder_cli_options(self.options)
    self.log.log_d('vm_builder_cli_handler: options={}'.format(self.options))
  
  def vm_builder_ssh_setup(self, ssh_config_dir, username, ssh_public_key, ssh_private_key, domain_name,
                           builder_access_ssh_public_key):
    'Setup ssh config inside a vm builder instance'
    check.check_string(ssh_config_dir)
    check.check_string(username)
    check.check_string(ssh_public_key)
    check.check_string(ssh_private_key)
    check.check_string(domain_name)
    check.check_string(builder_access_ssh_public_key)

    self.log.log_d('vm_builder_ssh_setup: ssh_config_dir={} username={}'.format(ssh_config_dir,
                                                                                 username))
    cm = ssh_config_manager(ssh_config_dir)

    # Install outbound keys needed for git push and pull from domain_name
    ssh_public_key_content = file_util.read(ssh_public_key, codec = 'utf-8')
    ssh_private_key_content = file_util.read(ssh_private_key, codec = 'utf-8')
    installed = cm.install_key_pair_for_host(ssh_public_key_content,
                                             ssh_private_key_content,
                                             domain_name,
                                             username = username,
                                             include_ip_address = not self.options.dont_include_ip_address,
                                             include_comment = not self.options.dont_include_comment)
    self.log.log_d('vm_builder_ssh_setup: bitbucket installed={}'.format(installed))

    # Install inbound keys to ssh into the vm builder from the vm host
    builder_access_ssh_public_key_content = file_util.read(builder_access_ssh_public_key, codec = 'utf-8')
    installed = cm.install_public_key(builder_access_ssh_public_key_content, 'vm_builder_access_key', True)
    self.log.log_d('vm_builder_ssh_setup: access installed={}'.format(installed))
    return 0

  def vm_host_ssh_setup(self, ssh_config_dir, filename, username,
                        builder_access_ssh_public_key, builder_access_ssh_private_key):
    'Setup ssh config inside a vm host instance'
    check.check_string(ssh_config_dir)
    check.check_string(filename)
    check.check_string(username)
    check.check_string(builder_access_ssh_public_key)
    check.check_string(builder_access_ssh_private_key)
    
    self.log.log_d('vm_host_ssh_setup: ssh_config_dir={} filename={} username={}'.format(ssh_config_dir,
                                                                                          filename,
                                                                                          username))
    
    cm = ssh_config_manager(ssh_config_dir)

    # Install inbound keys to ssh into the vm builder from the vm host
    builder_access_ssh_public_key_content = file_util.read(builder_access_ssh_public_key, codec = 'utf-8')
    builder_access_ssh_private_key_content = file_util.read(builder_access_ssh_private_key, codec = 'utf-8')
    installed = cm.install_key_pair(builder_access_ssh_public_key_content,
                                    builder_access_ssh_private_key_content,
                                    filename)
    self.log.log_d('vm_builder_ssh_setup: access installed={}'.format(installed))
    return 0
