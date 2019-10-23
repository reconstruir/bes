#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from .git_clone_options import git_clone_options

class git_repo_script_options(git_clone_options):
  
  def __init__(self, *args, **kargs):
    super(git_repo_script_options, self).__init__(*args, **kargs)
    self.push = False
    self.bump_tag_component = None
    self.dry_run = False
    self.debug = False
    self.verbose = False
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.push)
    check.check_string(self.bump_tag_component, allow_none = True)
    check.check_bool(self.dry_run)
    check.check_bool(self.debug)
    check.check_bool(self.verbose)

check.register_class(git_repo_script_options)
