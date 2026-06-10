#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path

from bes.bcli.bcli_command_handler import bcli_command_handler

from .archiver import archiver
from .archive_util import archive_util

class archive_command_handler(bcli_command_handler):

  def name(self):
    return 'archive'

  def _command_remove_members(self, archive, members, options):
    archive_util.remove_members(archive, members)
    return 0

  def _command_contents(self, archives, options):
    if len(archives) == 1:
      self._do_contents_one_archive(archives[0], False)
    else:
      for a in archives:
        self._do_contents_one_archive(a, True)
    return 0

  @classmethod
  def _do_contents_one_archive(clazz, archive, print_archive):
    for member in archiver.members(archive):
      if print_archive:
        print('{}:{}'.format(path.basename(archive), member))
      else:
        print(member)

  def _command_duplicates(self, archives, check_content, options):
    dups = archive_util.duplicate_members(archives, only_content_conficts=check_content)
    for member, archives in sorted(dups.items()):
      print('{}: {}'.format(member, ' '.join(archives)))
    return 0

  def _command_extract(self, archives, dest_dir, options):
    for archive in archives:
      archiver.extract_all(archive, dest_dir)
    return 0

  def _command_extract_file(self, archive_filename, filename, output_filename, options):
    if not output_filename:
      output_filename = path.join(os.getcwd(), path.basename(filename))
    archiver.extract_member_to_file(archive_filename, filename, output_filename)
    return 0

  def _command_cat(self, archive_filename, filename, options):
    s = archiver.extract_member_to_string(archive_filename, filename, codec='utf-8')
    print(s)
    return 0

  def _command_combine(self, dest_archive, archives, check_content, base_dir, exclude, options):
    archive_util.combine(archives, dest_archive,
                         check_content=check_content,
                         base_dir=base_dir,
                         exclude=exclude)
    return 0

  def _command_diff(self, archive1, archive2, options):
    rv = archive_util.diff_contents(archive1, archive2)
    return self._print_diff_output(rv)

  def _command_diff_manifest(self, archive1, archive2, options):
    rv = archive_util.diff_manifest(archive1, archive2)
    return self._print_diff_output(rv)

  def _command_diff_dir(self, dir1, dir2, options):
    rvs = archive_util.diff_dir(dir1, dir2)
    result = 0
    for rv in rvs:
      if rv.execute_result.exit_code != 0:
        print('{}: different'.format(rv.filename))
        self._print_diff_output(rv.execute_result)
        result = 1
    return result

  def _command_search(self, archive, text, ignore_case, whole_word, options):
    rv = archive_util.search(archive, text, ignore_case=ignore_case, whole_word=whole_word)
    print(rv.stdout)
    return rv.exit_code

  @classmethod
  def _print_diff_output(clazz, rv):
    if rv.stdout.strip():
      print(rv.stdout)
    return rv.exit_code
