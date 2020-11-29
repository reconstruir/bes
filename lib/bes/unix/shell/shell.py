#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.env_var import os_env_var
from bes.system.host import host
from bes.system.user import user
from bes.text.text_line_parser import text_line_parser
from bes.fs.file_util import file_util
from bes.unix.sudo.sudo import sudo
from bes.unix.sudo.sudo_cli_options import sudo_cli_options
from bes.system.log import logger

from .shell_error import shell_error

class shell(object):
  'Class to deal with unix shells.'

  _log = logger('shell')
  
  @classmethod
  def shell_is_bash(clazz):
    'Return True if the current shell is bash.'
    return 'bash' in clazz.shell_for_user()

  @classmethod
  def shell_for_user(clazz, username = None):
    'Return the shell for the given user.'
    username = username or user.USERNAME
    if host.is_unix():
      return clazz._shell_for_user_unix(username)
    else:
      host.raise_unsupported_system()

  @classmethod
  def _shell_for_user_unix(clazz, username):
    import pwd
    return pwd.getpwnam(username).pw_shell

  @classmethod
  def has_shell(clazz, shell):
    'Return True if shell is valid.'
    return shell in clazz.valid_shells()
  
  @classmethod
  def valid_shells(clazz):
    'Return a list if valid shells.'
    content = file_util.read('/etc/shells', codec = 'utf-8')
    return text_line_parser.parse_lines(content, strip_comments = True, strip_text = True, remove_empties = True)

  @classmethod
  def change_shell(clazz, new_shell, sudo_password = None):
    'Change the shell.'
    if not clazz.has_shell(new_shell):
      raise shell_error('Invalid shell: "{}"'.format(new_shell))
    cmd = [
      'chsh',
      '-s', new_shell,
      user.USERNAME,
    ]
    sudo_options = sudo_cli_options()
    sudo_options.error_message = 'Failed to read sudo password for chsh.'
    sudo_options.prompt = 'sudo password for chsh: '
    sudo_options.password = sudo_password
    clazz._log.log_d('_sudo_auth: calling sudo if needed: options={}'.format(sudo_options))
    sudo.call_sudo(cmd, options = sudo_options)
