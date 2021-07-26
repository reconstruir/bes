#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.cli.cli_command_handler import cli_command_handler
from bes.system.log import logger

from .git_dir import git_dir
from .git_download import git_download
from .git_output import git_output
from .git_repo import git_repo
from .git_repo_status_options import git_repo_status_options
from .git_status_getter import git_status_getter
from .git_util import git_util

class git_status_cli_handler(cli_command_handler):

  _log = logger('git_status')
  
  def __init__(self, cli_args):
    super(git_status_cli_handler, self).__init__(cli_args, options_class = git_repo_status_options)
    check.check_git_repo_status_options(self.options)
    self._log.log_d('options={}'.format(self.options))
  
  def get(self, dirs):
    check.check_string_seq(dirs)

    git_dirs = git_dir._resolve_git_dirs(dirs)
    repos = [ git_repo(d) for d in git_dirs ]

    result = git_status_getter.get_status(repos, options = self.options)

    for next_repo, next_status in result.items():
      self._print_status2(next_repo, next_status, self.options)
    
    return 0

  @classmethod
  def _print_status2(self, repo, status, options):
    check.check_git_repo(repo)
    check.check_git_repo_status(status)
    check.check_git_repo_status_options(options)

    branch_status = status.branch_status
    has_changes = len(status.change_status) > 0
    has_branch_status = branch_status.behind != 0 or branch_status.ahead != 0
    if True in [ has_changes, has_branch_status, options.force_show ]:
      blurb = [ repo.root.replace(path.expanduser('~'), '~'), repo.remote_get_url() ]
      blurb.append(status.last_commit.commit_hash_short)
      branch_status_blurb = [ '*' + status.active_branch ]
      if branch_status.ahead != 0:
        branch_status_blurb.append('ahead %d' % (branch_status.ahead))
      if branch_status.behind != 0:
        branch_status_blurb.append('behind %d' % (branch_status.behind))
      if branch_status_blurb:
        blurb.append('[%s]' % (', '.join(branch_status_blurb)))

      print('%s:' % (' '.join(blurb)))
      for item in status.change_status:
        print('  %3s %s' % (item.action, item.filename))
      print('')
