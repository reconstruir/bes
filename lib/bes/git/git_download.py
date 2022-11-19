# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, re, time
from datetime import datetime
from collections import namedtuple

from ..fs.file_util import file_util
from ..fs.temp_file import temp_file
from ..ssh_config.ssh_config_manager import ssh_config_manager
from ..system.check import check
from ..system.env_override import env_override
from ..system.environment import environment
from ..system.log import logger

from .git_config import git_config
from .git_download_options import git_download_options
from .git_error import git_error
from .git_remote import git_remote
from .git_repo import git_repo

class git_download(object):
  'A class to deal with downloading revision tarballs wholesale.'

  _log = logger('git_download')

  @classmethod
  def download(clazz, address, revision, output_filename = None,
               base_name = None, download_options = None):
    'Download abstraction for a git repo that wraps cloning, archiving and optionally an temp ssh setup.'
    check.check_string(address)
    check.check_string(revision)
    check.check_string(base_name, allow_none = True)
    check.check_string(output_filename, allow_none = True)

    download_options = download_options or git_download_options()
    
    clazz._log.log_method_d()
    parsed_address = git_remote.parse(address)
    name = parsed_address.project
    if not base_name:
      base_name = '{}-{}'.format(name, revision)

    if not output_filename:
      output_filename = '{}.tar.gz'.format(base_name)

    clazz._log.log_d('name={} base_name={} output_filename={}'.format(name,
                                                                      base_name,
                                                                      output_filename))
    download_options = download_options or git_download_options()

    if download_options.has_ssh_credentials():
      ssh_credentials = download_options.ssh_credentials()
      clazz._do_download_with_temp_ssh(address, revision, output_filename, base_name,
                                       download_options, parsed_address, ssh_credentials)
    else:
      clazz._do_download(address, revision, output_filename, base_name, download_options)
    return output_filename

  @classmethod
  def _do_download(clazz, address, revision, output_filename,
                   base_name, download_options):
    clazz._log.log_d('_do_download: home={} real_home={}'.format(path.expanduser('~'),
                                                                 environment.home_dir()))
    tmp_root_dir = temp_file.make_temp_dir(delete = not download_options.debug)
    if download_options.debug:
      print('tmp_root_dir={}'.format(tmp_root_dir))
    repo = git_repo(tmp_root_dir, address = address)
    repo.clone(options = download_options)
    repo.archive_to_file(base_name, revision, output_filename, archive_format = 'tgz')

  @classmethod
  def _do_download_with_temp_ssh(clazz, address, revision, output_filename,
                                 base_name, download_options, parsed_address,
                                 ssh_credentials):
    domain_name = parsed_address.service
    clazz._log.log_d('_do_download_with_temp_ssh: domain_name={}'.format(domain_name))

    temp_home = temp_file.make_temp_dir(delete = not download_options.debug)
    if download_options.debug:
      print('temp_home={}'.format(temp_home))
    temp_ssh_dir = path.join(temp_home, '.ssh')
    clazz._log.log_d('_do_download_with_temp_ssh: temp_ssh_dir={}'.format(temp_ssh_dir))
    cm = ssh_config_manager(temp_ssh_dir)

    installed = cm.install_key_pair_for_host(ssh_credentials.public_key,
                                             ssh_credentials.private_key,
                                             domain_name,
                                             username = ssh_credentials.username,
                                             host_key_type = ssh_credentials.host_key_type,
                                             include_ip_address = True,
                                             include_comment = True)
    # use a temporary HOME with custom git and ssh config just for this download
    with env_override.temp_home(use_temp_home = temp_home) as env:
      git_config.set_identity('test', 'test@example.com')
      ssh_config_file = path.join(temp_ssh_dir, 'config')
      ssh_command = 'ssh -F {}'.format(ssh_config_file)
      git_config.set_value('core.sshCommand', ssh_command)
      clazz._do_download(address, revision, output_filename, base_name, download_options)
      file_util.remove(temp_home)
