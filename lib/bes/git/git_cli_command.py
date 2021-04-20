#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.common.string_util import string_util
from bes.common.table import table
from bes.git.git import git
from bes.git.git_ref_where import git_ref_where
from bes.git.git_repo import git_repo
from bes.text.text_box import text_box_colon
from bes.text.text_box import text_box_unicode
from bes.text.text_table import text_cell_renderer
from bes.text.text_table import text_table
from bes.text.text_table import text_table_style
from bes.version.software_version import software_version

from .git_cli_options import git_cli_options
from .git_cli_util import git_cli_util
from .git_output import git_output
from .git_tag import git_tag_list

class git_cli_command(cli_command_handler):

  def __init__(self, cli_args):
    super(git_cli_command, self).__init__(cli_args, options_class = git_cli_options)
    check.check_git_cli_options(self.options)

  _DELTA_MAP = {
    'major': [ 1, 0, 0 ],
    'minor': [ 0, 1, 0 ],
    'revision': [ 0, 0, 1 ],
  }
  
  def bump_tag(self, component, dont_push, reset_lower, prefix):
    check.check_string(component, allow_none = True)
    check.check_bool(dont_push)
    check.check_bool(reset_lower)
    check.check_string(prefix, allow_none = True)

    repo = git_repo(self.options.root_dir)
    old_tag = repo.greatest_local_tag(prefix = prefix)
    bump_rv = repo.bump_tag(component,
                            push = not dont_push,
                            dry_run = self.options.dry_run,
                            reset_lower = reset_lower,
                            prefix = prefix)
    blurb = 'old_tag={} new_tag={}'.format(bump_rv.old_tag, bump_rv.new_tag)
    if self.options.dry_run:
      print('dry_run: {} dont_push={}'.format(blurb, dont_push))
    if self.options.verbose:
      print(blurb)
    return 0

  @classmethod
  def delete_tags(self, tags, local, remote, from_file):
    check.check_bool(local, allow_none = True)
    check.check_string_seq(tags)
    check.check_bool(remote, allow_none = True)
    check.check_string(from_file, allow_none = True)
    
    where = git_ref_where.determine_where(local, remote)

    combined_tags = []
    
    if from_file:
      next_tags = git_cli_util.read_tag_list_file(from_file)
      combined_tags.extend(next_tags)
      
    if tags:
      combined_tags.extend(tags)
      
    for tag in combined_tags:
      git.delete_tag(self.options.root_dir, tag, where, self.options.dry_run)
    return 0

  def tags(self, local, remote, prefix, limit, sort_type, reverse):
    check.check_bool(local, allow_none = True)
    check.check_bool(remote, allow_none = True)
    check.check_string(prefix, allow_none = True)
    check.check_int(limit, allow_none = True)
    check.check_string(prefix, allow_none = True)
    check.check_string(sort_type, allow_none = True)
    check.check_bool(reverse)

    r = git_repo(self.options.root_dir)
    tags = r.list_tags(sort_type = sort_type, reverse = reverse, limit = limit, prefix = prefix)
    
#    return
#    where = git_ref_where.determine_where(local, remote)
#    if where == 'both':
#      clazz._list_tags_both(self.options)
#      return 0
#    if where == 'local':
#      tags = git.list_local_tags(self.options.root_dir)
#    else:
#      tags = git.list_remote_tags(self.options.root_dir)
    tags.output(self.options.output_style, output_filename = self.options.output_filename)
    return 0
  
  def _list_tags_both(self):
    local_tags = git.list_local_tags(self.options.root_dir)
    remote_tags = git.list_remote_tags(self.options.root_dir)
    slocal = set(local_tags)
    sremote = set(remote_tags)

    sboth = software_version.sort_versions(list(slocal & sremote))
    slocal_only = slocal - sremote
    sremote_only = sremote - slocal

    data = []
    for tag in sboth:
      if tag in sboth:
        tag_where = 'both'
      elif tag in slocal_only:
        tag_where = 'local'
      elif tag in sremote_only:
        tag_where = 'remote'
      data.append( ( tag, tag_where ) )
    if not data:
      return 0
    tt = text_table(data = data)
    tt.set_labels( ( 'TAG', 'WHERE' ) )
    print(tt)
    return 0

  def tag(self, tag, local, remote, commit):
    check.check_bool(local, allow_none = True)
    check.check_bool(remote, allow_none = True)
    check.check_string(commit, allow_none = True)
    
    where = git_ref_where.determine_where(local, remote)
    if not tag:
      self._tag_print(self.options.root_dir, where)
    else:
      self._tag_set(self.options.root_dir, tag, where, commit)
    return 0
    
  @classmethod
  def _tag_print(clazz, root_dir, where):
    messages = []
    if where in [ 'local', 'both' ]:
      greatest_tag = git.greatest_local_tag(root_dir)
      msg = ' local: {tag}'.format(tag = greatest_tag.name if greatest_tag else '')
      messages.append(msg)
    if where in [ 'remote', 'both' ]:
      greatest_tag = git.greatest_remote_tag(root_dir)
      msg = 'remote: {tag}'.format(tag = greatest_tag.name if greatest_tag else '')
      messages.append(msg)
    for msg in messages:
      print(msg)

  @classmethod
  def _tag_set(clazz, root_dir, tag, where, commit):
    git.tag(root_dir, tag, allow_downgrade = True, commit = commit)
    git.push_tag(root_dir, tag)
    
  def retag(self, tag = None):
    tag = tag or git.greatest_local_tag(self.options.root_dir)
    git.delete_tag(self.options.root_dir, tag, 'both', False)
    git.tag(self.options.root_dir, tag)
    git.push_tag(self.options.root_dir, tag)
    if self.options.verbose:
      print('old_tag={} new_tag={}'.format(tag, tag))
    return 0

  class branch_active_cell_renderer(text_cell_renderer):
    def __init__(self, *args, **kargs):
      super(git_cli_command.branch_active_cell_renderer, self).__init__(*args, **kargs)
    def render(self, value, width = None, is_label = False):
      if is_label:
        return value
      return '*' if value else ' '
      
  class branch_ahead_behind_cell_renderer(text_cell_renderer):
    def __init__(self, *args, **kargs):
      super(git_cli_command.branch_ahead_behind_cell_renderer, self).__init__(*args, **kargs)
    def render(self, value, width = None, is_label = False):
      if is_label:
        return value
      return str(value).center(2) if value else ' ' * 2
      
  def branches(self, local, remote, difference, no_fetch):
    check.check_bool(local, allow_none = True)
    check.check_bool(remote, allow_none = True)
    check.check_bool(difference)
    check.check_bool(no_fetch)
    
    where = git_ref_where.determine_where(local, remote)
    if not no_fetch:
      git.fetch(self.options.root_dir)
    branches = git.list_branches(self.options.root_dir, where)
#    # sort the branches using software version so numeric versions of branch sort properly
#    branches.sort(key = lambda b: tuple(list(software_version.parse_version(b.name)) + [ b.name, b.where ]) )
    if difference:
      for branch in branches.difference:
        print(branch)
      return 0
    if self.options.output_style == 'brief':
      for branch in branches.names:
        print(branch)
      return 0
    title = git.remote_origin_url(self.options.root_dir)
    self._print_branches(title, branches, branches.longest_name, branches.longest_comment,
                          self.options.output_style)
    return 0

  def _print_branches(self, title, branches, longest_name, longest_comment, style):
    longest_comment = 60
    if not branches:
      return

    if style == 'plain':
      style = text_table_style(spacing = 1, box = text_box_colon())
    else:
      style = text_table_style(spacing = 1, box = text_box_unicode())

    r = { 'AHEAD': 'AH', 'BEHIND': 'BE', 'ACTIVE': '*' }
    labels = tuple([ string_util.replace(f.upper(), r) for f in branches[0]._fields ])

    t = table(data = branches)
    t.column_names = labels
    tt = text_table(data = t, style = style)
    if not style == 'plain':
      tt.set_title(title)
      tt.set_labels(labels)
    tt.set_col_renderer('NAME', text_cell_renderer(width = longest_name))
    tt.set_col_renderer('*', self.branch_active_cell_renderer())
    tt.set_col_renderer('AH', self.branch_ahead_behind_cell_renderer())
    tt.set_col_renderer('BE', self.branch_ahead_behind_cell_renderer())
    tt.set_col_renderer('COMMENT', text_cell_renderer(width = longest_comment))
    print(tt)

  def short_commit(self, commit):
    short_commit = git.short_hash(self.options.root_dir, commit)
    print(short_commit)
    return 0

  def long_commit(self, commit):
    long_commit = git.long_hash(self.options.root_dir, commit)
    print(long_commit)
    return 0
