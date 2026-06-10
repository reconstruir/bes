# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command import cli_command

from bes.archive.archive_cli_args import archive_cli_args
from bes.bes_project.bes_project_cli_args import bes_project_cli_args
from bes.fs.dir_combine_cli_args import dir_combine_cli_args
from bes.fs.dir_partition_cli_args import dir_partition_cli_args
from bes.fs.dir_split_cli_args import dir_split_cli_args
from bes.fs.dirs_cli_args import dirs_cli_args
from bes.fs.file_duplicates_cli_args import file_duplicates_cli_args
from bes.fs.file_split_cli_args import file_split_cli_args
from bes.fs.files_cli_args import files_cli_args
from bes.mermaid.mermaid_cli_args import mermaid_cli_args
from bes.native_package.native_package_cli_args import native_package_cli_args
from bes.properties_file_v2.properties_file_cli_args import properties_file_cli_args
from bes.pyinstaller.pyinstaller_cli_args import pyinstaller_cli_args
from bes.python.pip_cli_args import pip_cli_args
from bes.python.pip_installer_cli_args import pip_installer_cli_args
from bes.python.pip_project_cli_args import pip_project_cli_args
from bes.python.python_cli_args import python_cli_args
from bes.python_installer.python_installer_cli_args import python_installer_cli_args

from .system_cli_args import system_cli_args
  
COMMON_COMMAND_GROUPS = [
  cli_command('archive', 'archive_add_args', 'Deal with archive', archive_cli_args),
  cli_command('bes_project', 'bes_project_add_args', 'Bes project stuff', bes_project_cli_args),    
  cli_command('dir_combine', 'dir_combine_add_args', 'Directory combine', dir_combine_cli_args),
  cli_command('dir_partition', 'dir_partition_add_args', 'Directory partition', dir_partition_cli_args),
  cli_command('dir_split', 'dir_split_add_args', 'Directory split', dir_split_cli_args),
  cli_command('dirs', 'dirs_add_args', 'Directory stuff', dirs_cli_args),
  cli_command('file_duplicates', 'file_duplicates_add_args', 'Directory partition', file_duplicates_cli_args),
  cli_command('file_split', 'file_split_add_args', 'Directory partition', file_split_cli_args),
  cli_command('files', 'files_add_args', 'File stuff', files_cli_args),
  cli_command('mermaid', 'mermaid_add_args', 'Mermaid python code', mermaid_cli_args),
  cli_command('native_package', 'native_package_add_args', 'Deal with native packages', native_package_cli_args),
  cli_command('pip', 'pip_add_args', 'Pip stuff', pip_cli_args),
  cli_command('pip_installer', 'pip_installer_add_args', 'Pip installer stuff', pip_installer_cli_args),
  cli_command('pip_project', 'pip_project_add_args', 'Pip project stuff', pip_project_cli_args),
  cli_command('properties_file', 'properties_file_add_args', 'Deal with properties files', properties_file_cli_args),
  cli_command('pyinstaller', 'pyinstaller_add_args', 'Deal with PyInstaller', pyinstaller_cli_args),
  cli_command('python', 'python_add_args', 'Deal with python', python_cli_args),
  cli_command('python_installer', 'python_installer_add_args', 'Deal with python install', python_installer_cli_args),
  cli_command('shell_framework', 'shell_framework_add_args', 'Deal with the bes_shell framework', shell_framework_cli_args),
]
