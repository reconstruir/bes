# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.property.cached_property import cached_property
from bes.git.git_commit_hash import git_commit_hash

#* Label: Command Line Tools for Xcode-12.2
#	Title: Command Line Tools for Xcode, Version: 12.2, Size: 440907K, Recommended: YES,
class software_updater_item(namedtuple('software_updater_item', 'title, label, version, size, recommended')):
  'A class to deal with a single macos softwareupdater item.'
  
  def __new__(clazz, ref_type, revision, author, date):
    check.check_string(ref_type)
    check.check_string(revision)
    check.check_string(author)
    check.check_string(date)

    return clazz.__bases__[0].__new__(clazz, ref_type, revision, author, date)

  @cached_property
  def revision_short(self):
    'Return a short revision'
    return git_commit_hash.shorten(self.revision)
