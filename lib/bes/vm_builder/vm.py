# -*- coding: utf-8 -*-
""""This module contains the business logic for VM Builder manager for MacOS."""

import os
import glob
import subprocess
from io import open

from bes.fs.file_util import file_util
from bes.system.execute import execute
from bes.vault.vault_ego import vault_ego
from bes.vault.vault_cli_command import vault_cli_command
from bes.ssh.ssh_config_manager import ssh_config_manager

class vm_manager(object):
  """The main purpose of this class is to manage VM Builder stuff for MacOS, such as configuration
  of proper SSH (public and private keys, autorized_keys, known_hosts and config), etc.

  Args:
    role: Vault role ID.
          Default value is None (this means that EGO_VAULT_ROLE_ID environment variable must be set).
    secret: Vault secret ID.
            Default value is None (this means that EGO_VAULT_SECRET_ID environment variable must be set).

            To get detailed explanation about EGO_VAULT_ROLE_ID and EGO_VAULT_SECRET_ID usage read this document -
            https://confluence.corp.imvu.com/display/~akarpenko/Egoist+CLI+and+Google+Services#EgoistCLIandGoogleServices-GetcredentialsandtokenfromVault

  Attributes:
    vault_config: Vault config object which helps to use vault via CLI commands.
  """
  _vm_user = '/Users/vagrant'

  def __init__(self, role=None, secret=None):
    self.vault_config = vault_ego.resolve_config(vault_ego.DEFAULT_BASE_URL, vault_ego.DEFAULT_CACHE_DIR, role, secret)

  @staticmethod
  def _create_file(file_name, content):
    if isinstance(content, bytes):
      content = content.decode('utf-8')

    with open(file_name, 'w', encoding='utf-8') as file:
      try:
        file.write(unicode(content))
      except NameError:
        file.write(content)

  def _save_ssh_keys(self):
    private_key_file_name = '{}/.ssh/id_rsa'.format(self._vm_user)
    public_key_file_name = '{}/.ssh/id_rsa.pub'.format(self._vm_user)

    vault_cli_command.get(self.vault_config, 'cicd/bitbucket', 'EGO_BITBUCKET_SSH_PRIVATE_KEY', False, private_key_file_name)
    vault_cli_command.get(self.vault_config, 'cicd/bitbucket', 'EGO_BITBUCKET_SSH_PUBLIC_KEY', False, public_key_file_name)

  def setup_ssh(self):
    """Setup SSH stuff for VM Builder (for MacOS):
    - export updated PATH variable
    - create id_rsa file
    - create id_rsa.pub file
    - create authorized_keys file
    - create config file
    - create know_hosts
    - chmod 700 ~/.ssh/*

    Returns:
      None.

    Raises:
      ValueError: If ssh-keyscan tool failed.
    """
    env = os.environ.copy()
    env['PATH'] = '{}/tools/bin:{}'.format(self._vm_user, env['PATH'])

    self._save_ssh_keys()
    public_ssh_key = file_util.read('{}/.ssh/id_rsa.pub'.format(self._vm_user), codec='utf-8')
    authorized_keys_content = public_ssh_key.replace('bitbckt-org-wm-bldr-prod-20190201', 'vagrant')

    result = execute.execute(['ssh-keyscan', '-t', 'rsa', 'bitbucket.org'], env=env)
    output, errors = result.stdout, result.stderr

    if errors:
      ValueError('ssh-keyscan failed [{}]'.format(str(errors)))

    self._create_file('{}/.ssh/authorized_keys'.format(self._vm_user), authorized_keys_content)
    self._create_file('{}/.ssh/config'.format(self._vm_user), 'Host *\n  UseKeychain yes')
    self._create_file('{}/.ssh/known_hosts'.format(self._vm_user), output)

    ssh_files = glob.glob('{}/.ssh/*'.format(self._vm_user))
    for ssh_file in ssh_files:
      subprocess.call(['chmod', '700', ssh_file])
