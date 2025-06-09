# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command import cli_command

from bes.archive.archive_cli_args import archive_cli_args
from bes.bes_project.bes_project_cli_args import bes_project_cli_args
from bes.docker.docker_cli_args import docker_cli_args
from bes.egg.egg_cli_args import egg_cli_args
from bes.fs.dir_combine_cli_args import dir_combine_cli_args
from bes.fs.dir_partition_cli_args import dir_partition_cli_args
from bes.fs.dir_split_cli_args import dir_split_cli_args
from bes.fs.dirs_cli_args import dirs_cli_args
from bes.fs.file_duplicates_cli_args import file_duplicates_cli_args
from bes.fs.file_split_cli_args import file_split_cli_args
from bes.fs.files_cli_args import files_cli_args
from bes.git.git_cli_args import git_cli_args
from bes.git.git_download_cli_args import git_download_cli_args
from bes.git.git_identity_cli_args import git_identity_cli_args
from bes.git.git_projects_cli_args import git_projects_cli_args
from bes.git.git_repo_cli_args import git_repo_cli_args
from bes.git.git_repo_document_cli_args import git_repo_document_cli_args
from bes.git.git_repo_script_cli_args import git_repo_script_cli_args
from bes.mermaid.mermaid_cli_args import mermaid_cli_args
from bes.native_package.native_package_cli_args import native_package_cli_args
from bes.pipenv_project.pipenv_project_cli_args import pipenv_project_cli_args
from bes.properties_file_v2.properties_file_cli_args import properties_file_cli_args
from bes.pyinstaller.pyinstaller_cli_args import pyinstaller_cli_args
from bes.python.pip_cli_args import pip_cli_args
from bes.python.pip_installer_cli_args import pip_installer_cli_args
from bes.python.pip_project_cli_args import pip_project_cli_args
from bes.python.python_cli_args import python_cli_args
from bes.python_installer.python_installer_cli_args import python_installer_cli_args
from bes.refactor.refactor_cli_args import refactor_cli_args
from bes.shell_framework.shell_framework_cli_args import shell_framework_cli_args
from bes.vm_builder.vm_builder_cli_args import vm_builder_cli_args
from bes.vmware.vmware_app_cli_args import vmware_app_cli_args
from bes.vmware.vmware_cli_args import vmware_cli_args
from bes.vmware.vmware_client_cli_args import vmware_client_cli_args
from bes.vmware.vmware_preferences_cli_args import vmware_preferences_cli_args
from bes.vmware.vmware_server_cli_args import vmware_server_cli_args
from bes.vmware.vmware_session_cli_args import vmware_session_cli_args

from ..btl.btl_cli_args import btl_cli_args

from .system_cli_args import system_cli_args
  
COMMON_COMMAND_GROUPS = [
  cli_command('archive', 'archive_add_args', 'Deal with archive', archive_cli_args),
  cli_command('bes_project', 'bes_project_add_args', 'Bes project stuff', bes_project_cli_args),    
  cli_command('dir_combine', 'dir_combine_add_args', 'Directory combine', dir_combine_cli_args),
  cli_command('dir_partition', 'dir_partition_add_args', 'Directory partition', dir_partition_cli_args),
  cli_command('dir_split', 'dir_split_add_args', 'Directory split', dir_split_cli_args),
  cli_command('dirs', 'dirs_add_args', 'Directory stuff', dirs_cli_args),
  cli_command('docker', 'docker_add_args', 'Docker stuff', docker_cli_args),
  cli_command('egg', 'egg_add_args', 'Deal with eggs', egg_cli_args),
  cli_command('file_duplicates', 'file_duplicates_add_args', 'Directory partition', file_duplicates_cli_args),
  cli_command('file_split', 'file_split_add_args', 'Directory partition', file_split_cli_args),
  cli_command('files', 'files_add_args', 'File stuff', files_cli_args),
  cli_command('git', 'git_add_args', 'Deal with git', git_cli_args),
  cli_command('git_download', 'git_download_add_args', 'Deal with git downloads', git_download_cli_args),
  cli_command('git_identity', 'git_identity_add_args', 'Deal with git identity', git_identity_cli_args),
  cli_command('git_projects', 'git_projects_add_args', 'Deal with git projects', git_projects_cli_args),    
  cli_command('git_repo', 'git_repo_add_args', 'Deal with git repos', git_repo_cli_args),
  cli_command('git_repo_document', 'git_repo_document_add_args', 'Deal with git documents', git_repo_document_cli_args),
  cli_command('git_repo_script', 'git_repo_script_add_args', 'Deal with git repo scipts', git_repo_script_cli_args),
  cli_command('mermaid', 'mermaid_add_args', 'Mermaid python code', mermaid_cli_args),
  cli_command('native_package', 'native_package_add_args', 'Deal with native packages', native_package_cli_args),
  cli_command('pip', 'pip_add_args', 'Pip stuff', pip_cli_args),
  cli_command('pip_installer', 'pip_installer_add_args', 'Pip installer stuff', pip_installer_cli_args),
  cli_command('pip_project', 'pip_project_add_args', 'Pip project stuff', pip_project_cli_args),
  cli_command('pipenv_project', 'pipenv_project_add_args', 'Pipenv project stuff', pipenv_project_cli_args),
  cli_command('properties_file', 'properties_file_add_args', 'Deal with properties files', properties_file_cli_args),
  cli_command('pyinstaller', 'pyinstaller_add_args', 'Deal with PyInstaller', pyinstaller_cli_args),
  cli_command('python', 'python_add_args', 'Deal with python', python_cli_args),
  cli_command('python_installer', 'python_installer_add_args', 'Deal with python install', python_installer_cli_args),
  cli_command('refactor', 'refactor_add_args', 'Refactor python code', refactor_cli_args),
  cli_command('shell_framework', 'shell_framework_add_args', 'Deal with the bes_shell framework', shell_framework_cli_args),
  cli_command('vm_builder', 'vm_builder_add_args', 'VM Builder stuff', vm_builder_cli_args),
  cli_command('vmware', 'vmware_add_args', 'Deal with vmware', vmware_cli_args),    
  cli_command('vmware_app', 'vmware_app_add_args', 'Deal with vmware app', vmware_app_cli_args),
  cli_command('vmware_client', 'vmware_client_add_args', 'Deal with vmware client', vmware_client_cli_args),
  cli_command('vmware_preferences', 'vmware_preferences_add_args', 'Deal with vmware preferences', vmware_preferences_cli_args),
  cli_command('vmware_server', 'vmware_server_add_args', 'Deal with vmware server', vmware_server_cli_args),
  cli_command('vmware_session', 'vmware_session_add_args', 'Deal with vmware session', vmware_session_cli_args),

  cli_command('btl', 'btl_add_args', 'Deal with text lexers', btl_cli_args),
]
