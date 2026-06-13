#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from bes.bcli.bcli_application import bcli_application

from ..archive.archive_command_factory import archive_command_factory
from ..bat_project.bat_project_command_factory import bat_project_command_factory
from ..best_cli.system_command_factory import system_command_factory
from ..files.checksum.bf_checksum_command_factory import bf_checksum_command_factory
from ..files.duplicates.bf_file_duplicates_command_factory import bf_file_duplicates_command_factory
from ..files.media_finder.bf_media_find_command_factory import bf_media_find_command_factory
from ..files.metadata.bf_metadata_command_factory import bf_metadata_command_factory
from ..files.resolve.bf_file_resolver_command_factory import bf_file_resolver_command_factory
from ..fs.dir_combine_command_factory import dir_combine_command_factory
from ..fs.dir_partition_command_factory import dir_partition_command_factory
from ..fs.dir_split_command_factory import dir_split_command_factory
from ..fs.dirs_command_factory import dirs_command_factory
from ..fs.file_duplicates_command_factory import file_duplicates_command_factory
from ..fs.file_split_command_factory import file_split_command_factory
from ..fs.files_command_factory import files_command_factory
from ..linux.attr.linux_attr_command_factory import linux_attr_command_factory
from ..macos.command_line_tools.command_line_tools_command_factory import command_line_tools_command_factory
from ..macos.defaults.defaults_command_factory import defaults_command_factory
from ..macos.scutil.scutil_command_factory import scutil_command_factory
from ..macos.softwareupdater.softwareupdater_command_factory import softwareupdater_command_factory
from ..macos.xattr_exe.xattr_exe_command_factory import xattr_exe_command_factory
from ..mermaid.mermaid_command_factory import mermaid_command_factory
from ..native_package.native_package_command_factory import native_package_command_factory
from ..properties_file_v2.properties_file_command_factory import properties_file_command_factory
from ..pyinstaller.pyinstaller_command_factory import pyinstaller_command_factory
from ..unix.sudo.sudo_command_factory import sudo_command_factory

class bes_application(bcli_application):

  #@abstractmethod
  def name(self):
    return 'bes'

  #@abstractmethod
  def parser_factories(self):
    return [
      archive_command_factory,
      bat_project_command_factory,
      bf_checksum_command_factory,
      bf_file_duplicates_command_factory,
      bf_media_find_command_factory,
      bf_metadata_command_factory,
      bf_file_resolver_command_factory,
      dir_combine_command_factory,
      dir_partition_command_factory,
      dir_split_command_factory,
      dirs_command_factory,
      file_duplicates_command_factory,
      file_split_command_factory,
      files_command_factory,
      command_line_tools_command_factory,
      defaults_command_factory,
      linux_attr_command_factory,
      mermaid_command_factory,
      native_package_command_factory,
      properties_file_command_factory,
      pyinstaller_command_factory,
      scutil_command_factory,
      softwareupdater_command_factory,
      sudo_command_factory,
      system_command_factory,
      xattr_exe_command_factory,
    ]
