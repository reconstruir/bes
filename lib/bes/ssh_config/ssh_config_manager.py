#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util
from bes.fs.file_util import file_util
from bes.system.user import user

from .ssh_authorized_key import ssh_authorized_key
from .ssh_authorized_keys_file import ssh_authorized_keys_file
from .ssh_config_file import ssh_config_file
from .ssh_key_scan import ssh_key_scan
from .ssh_known_host import ssh_known_host
from .ssh_known_hosts_file import ssh_known_hosts_file

class ssh_config_manager(object):
  'Class to manage ssh client installations'

  def __init__(self, dot_ssh_dir):
    self._dot_ssh_dir = dot_ssh_dir

    self._config_file = path.join(self._dot_ssh_dir, 'config')
    self._config = ssh_config_file(self._config_file)

    self._known_hosts_file = path.join(self._dot_ssh_dir, 'known_hosts')
    self._known_hosts = ssh_known_hosts_file(self._known_hosts_file)

    self._authorized_keys_file = path.join(self._dot_ssh_dir, 'authorized_keys')
    self._authorized_keys = ssh_authorized_keys_file(self._authorized_keys_file)
    
  def add_config_host(self, hostname, values):
    """
    Add a new host to the config file with values.

    hostname (str): The hostname to add
    values (key_value_list, dict, or str): The values for hostname

    Returns None
    """
    self._config.update_host(hostname, values)

  def add_known_host(self, hostnames, key_type, key, comment = None):
    'Add a new known_host to the config file.'
    check.check_string_seq(hostnames)
    check.check_string(key_type)
    check.check_string(key)
    check.check_string(comment, allow_none = True)

    known_host = ssh_known_host(hostnames, key_type, key, comment)
    self._known_hosts.add_known_host(known_host)

  def add_authorized_key(self, key_type, key, annotation):
    'Add a new authorized_key to the config file.'
    check.check_string(key_type)
    check.check_string(key)
    check.check_string(annotation)

    authorized_key = ssh_authorized_key(key_type, key, annotation)
    self._authorized_keys.add_authorized_key(authorized_key)
    
  def install_key_pair_for_host(self, public_key, private_key, hostname, username = None,
                                include_ip_address = True, include_comment = True):
    check.check_string(public_key)
    check.check_string(private_key)
    check.check_string(hostname)
    check.check_string(username, allow_none = True)
    check.check_bool(include_ip_address)
    check.check_bool(include_comment)

    known_host = ssh_key_scan.scan(hostname,
                                   include_ip_address = include_ip_address,
                                   include_comment = include_comment)
    self._known_hosts.add_known_host(known_host)
    
    filename = 'id_rsa_' + hostname.replace('.', '_')
    
    installed = self.install_key_pair(public_key, private_key, filename)
    
    values = {
      'IdentityFile': installed.private_key_filename,
      'Hostname': hostname,
      'User': username or user.USERNAME,
    }
    self._config.update_host(hostname, values)
    return installed
    
  _installed_key_pair = namedtuple('_installed_key_pair', 'public_key_filename, private_key_filename')
  def install_key_pair(self, public_key, private_key, filename):
    '''
    Install a ssh key pair with the following patterns:
    ${dit_ssh_dir}/${filename}
    ${dit_ssh_dir}/${filename}.pub
    '''
    check.check_string(public_key)
    check.check_string(private_key)
    check.check_string(filename)

    public_key_filename = path.join(self._dot_ssh_dir, filename + '.pub')
    private_key_filename = path.join(self._dot_ssh_dir, filename)
    file_util.save(public_key_filename, content = public_key, mode = 0o0600, codec = 'utf-8')
    file_util.save(private_key_filename, content = private_key, mode = 0o0600, codec = 'utf-8')

    return self._installed_key_pair(public_key_filename, private_key_filename)

  def install_public_key(self, public_key, filename, add_authorized_key):
    '''
    Install a public ssh key pair with the following pattern:
    ${dit_ssh_dir}/${filename}.pub
    '''
    check.check_string(public_key)
    check.check_string(filename)
    check.check_bool(add_authorized_key)

    public_key_filename = path.join(self._dot_ssh_dir, filename + '.pub')
    file_util.save(public_key_filename, content = public_key, mode = 0o0600, codec = 'utf-8')

    if add_authorized_key:
      authorized_key = ssh_authorized_key.parse_text(public_key)
      self.add_authorized_key(authorized_key.key_type,
                              authorized_key.key,
                              authorized_key.annotation)
    
    return public_key_filename
  
