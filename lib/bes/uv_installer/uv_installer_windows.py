#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from bes.system.check import check
from bes.system.env_var import env_var
from bes.system.execute import execute
from bes.system.log import logger
from bes.system.os_env import os_env

from . import uv_installer_base
from . import uv_installer_error

class uv_installer_windows(uv_installer_base.uv_installer_base):
  'uv installer for Windows using the official PowerShell install script.'

  _log = logger('uv_installer')
  _UV_INSTALL_URL = 'https://astral.sh/uv/install.ps1'

  def __init__(self, options):
    check.check_uv_installer_options(options)
    super().__init__(options)

  def install(self, version=None):
    check.check_string(version, allow_none=True)

    install_environment = os_env.clone_current_env()
    if version:
      env_var(install_environment, 'UV_VERSION').value = version
    install_dir = self.options.resolve_install_dir()
    env_var(install_environment, 'UV_INSTALL_DIR').value = install_dir

    if self.options.dry_run:
      self._log.log_d(f'install: dry_run: would install uv version={version} to {install_dir}')
      return

    if self.options.install_script:
      self._run_script(self.options.install_script, install_environment)
    else:
      self._run_remote_script(install_environment)

    exe = self.exe_path()
    if not exe:
      install_dir_str = self.options.resolve_install_dir()
      path_entries = os.environ.get('PATH', '').split(os.pathsep)
      if install_dir_str not in path_entries:
        print(f'Warning: uv installed to {install_dir_str} which is not on PATH')

  def uninstall(self):
    install_dir = self.options.resolve_install_dir()
    for name in ('uv.exe', 'uvx.exe'):
      candidate = path.join(install_dir, name)
      if path.isfile(candidate):
        if self.options.dry_run:
          self._log.log_d(f'uninstall: dry_run: would remove {candidate}')
        else:
          os.remove(candidate)

  def is_installed(self):
    return self.exe_path() is not None

  def installed_version(self):
    exe = self.exe_path()
    if not exe:
      return None
    rv = execute.execute([exe, '--version'],
                         raise_error=False,
                         stderr_to_stdout=True,
                         check_python_script=False)
    if rv.exit_code != 0:
      return None
    parts = rv.stdout.strip().split()
    return parts[1] if len(parts) >= 2 else None

  def exe_path(self):
    install_dir = self.options.resolve_install_dir()
    candidate = path.join(install_dir, 'uv.exe')
    if path.isfile(candidate):
      return candidate
    return None

  def _run_script(self, script_path, environment):
    execute.execute(['powershell', '-ExecutionPolicy', 'ByPass', '-File', script_path],
                    env=environment,
                    raise_error=True,
                    stderr_to_stdout=True,
                    check_python_script=False)

  def _run_remote_script(self, environment):
    cmd = f'irm {self._UV_INSTALL_URL} | iex'
    execute.execute(['powershell', '-ExecutionPolicy', 'ByPass', '-Command', cmd],
                    env=environment,
                    raise_error=True,
                    stderr_to_stdout=True,
                    check_python_script=False)
