#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.cli.argparser_handler import argparser_handler
from bes.common.string_util import string_util
from bes.common.table import table
from bes.git.git import git
from bes.text.text_table import text_cell_renderer
from bes.text.text_table import text_table
from bes.text.text_table import text_table_style
from bes.text.text_box import text_box_colon
from bes.text.text_box import text_box_unicode
from bes.version.software_version import software_version

from .git_cli_util import git_cli_util
from .git_cli_options import git_cli_options

class git_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    options = git_cli_options(**kargs)
    filtered_args = argparser_handler.filter_keywords_args(git_cli_options, kargs)
    func = getattr(git_cli_command, command)
    return func(options, **filtered_args)
  
  _DELTA_MAP = {
    'major': [ 1, 0, 0 ],
    'minor': [ 0, 1, 0 ],
    'revision': [ 0, 0, 1 ],
  }
  
  @classmethod
  def bump_tag(clazz, options, component, dry_run, dont_push, reset_lower, verbose):
    check.check_git_cli_options(options)
    old_tag = git.greatest_local_tag(options.root_dir)
    bump_rv = git.bump_tag(options.root_dir, component,
                           push = not dont_push,
                           dry_run = dry_run,
                           reset_lower = reset_lower)
    blurb = 'old_tag={} new_tag={}'.format(bump_rv.old_tag, bump_rv.new_tag)
    if dry_run:
      print('dry_run: {} dont_push={}'.format(blurb, dont_push))
    if verbose:
      print(blurb)
    return 0

  @classmethod
  def delete_tags(clazz, options, tags, local, remote, dry_run, from_file):
    check.check_git_cli_options(options)
    check.check_bool(local, allow_none = True)
    check.check_string_seq(tags)
    check.check_bool(remote, allow_none = True)
    check.check_string(from_file, allow_none = True)
    
    where = git.determine_where(local, remote)

    combined_tags = []
    
    if from_file:
      next_tags = git_cli_util.read_tag_list_file(from_file)
      combined_tags.extend(next_tags)
      
    if tags:
      combined_tags.extend(tags)
      
    for tag in combined_tags:
      git.delete_tag(options.root_dir, tag, where, dry_run)
    return 0

  @classmethod
  def tags(clazz, options, local, remote, prefix, limit, reverse):
    check.check_git_cli_options(options)
    check.check_bool(local, allow_none = True)
    check.check_bool(remote, allow_none = True)
    check.check_string(prefix, allow_none = True)
    check.check_int(limit, allow_none = True)
    check.check_bool(reverse)

    where = git.determine_where(local, remote)
    if where == 'both':
      clazz._list_tags_both(options.root_dir)
      return 0
    if where == 'local':
      tags = git.list_local_tags(options.root_dir)
    else:
      tags = git.list_remote_tags(options.root_dir)
    if prefix:
      tags = [ tag for tag in tags if tag.startswith(prefix) ]
    if reverse:
      tags = [ tag for tag in reversed(tags) ]
    if limit:
      tags = tags[0:limit]
    for tag in tags:
      print(tag)
    return 0
  
  @classmethod
  def _list_tags_both(clazz, root_dir):
    local_tags = git.list_local_tags(root_dir)
    remote_tags = git.list_remote_tags(root_dir)
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

  @classmethod
  def tag(clazz, options, tag, local, remote, commit):
    check.check_git_cli_options(options)
    check.check_bool(local, allow_none = True)
    check.check_bool(remote, allow_none = True)
    check.check_string(commit, allow_none = True)
    
    where = git.determine_where(local, remote)
    if not tag:
      clazz._tag_print(options.root_dir, where)
    else:
      clazz._tag_set(options.root_dir, tag, where, commit)
    return 0
    
  @classmethod
  def _tag_print(clazz, root_dir, where):
    messages = []
    if where in [ 'local', 'both' ]:
      msg = ' local: {tag}'.format(tag = git.greatest_local_tag(root_dir))
      messages.append(msg)
    if where in [ 'remote', 'both' ]:
      msg = 'remote: {tag}'.format(tag = git.greatest_remote_tag(root_dir))
      messages.append(msg)
    for msg in messages:
      print(msg)
    
  @classmethod
  def _tag_set(clazz, root_dir, tag, where, commit):
    git.tag(root_dir, tag, allow_downgrade = True, commit = commit)
    git.push_tag(root_dir, tag)
    
  @classmethod
  def retag(clazz, options, tag = None, verbose = False):
    check.check_git_cli_options(options)

    tag = tag or git.greatest_local_tag(options.root_dir)
    git.delete_tag(options.root_dir, tag, 'both', False)
    git.tag(options.root_dir, tag)
    git.push_tag(root_dir, tag)
    if verbose:
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
      
  @classmethod
  def branches(clazz, options, local, remote, brief, plain, difference, no_fetch):
    check.check_git_cli_options(options)
    check.check_bool(local, allow_none = True)
    check.check_bool(remote, allow_none = True)
    check.check_bool(brief)
    check.check_bool(plain)
    check.check_bool(difference)
    check.check_bool(no_fetch)
    
    where = git.determine_where(local, remote)
    if not no_fetch:
      git.fetch(options.root_dir)
    branches = git.list_branches(options.root_dir, where)
#    # sort the branches using software version so numeric versions of branch sort properly
#    branches.sort(key = lambda b: tuple(list(software_version.parse_version(b.name)) + [ b.name, b.where ]) )
    if difference:
      for branch in branches.difference:
        print(branch)
      return 0
    if brief:
      for branch in branches.names:
        print(branch)
      return 0
    title = git.remote_origin_url(options.root_dir)
    clazz._print_branches(title, branches, branches.longest_name, branches.longest_comment, plain)
    return 0

  @classmethod
  def _print_branches(clazz, title, branches, longest_name, longest_comment, plain):
    longest_comment = 60
    if not branches:
      return

    if plain:
      style = text_table_style(spacing = 1, box = text_box_colon())
    else:
      style = text_table_style(spacing = 1, box = text_box_unicode())

    r = { 'AHEAD': 'AH', 'BEHIND': 'BE', 'ACTIVE': '*' }
    labels = tuple([ string_util.replace(f.upper(), r) for f in branches[0]._fields ])

    t = table(data = branches)
    t.column_names = labels
    tt = text_table(data = t, style = style)
    if not plain:
      tt.set_title(title)
      tt.set_labels(labels)
    tt.set_col_renderer('NAME', text_cell_renderer(width = longest_name))
    tt.set_col_renderer('*', clazz.branch_active_cell_renderer())
    tt.set_col_renderer('AH', clazz.branch_ahead_behind_cell_renderer())
    tt.set_col_renderer('BE', clazz.branch_ahead_behind_cell_renderer())
    tt.set_col_renderer('COMMENT', text_cell_renderer(width = longest_comment))
    print(tt)

  @classmethod
  def short_commit(clazz, options, commit):
    check.check_git_cli_options(options)

    short_commit = git.short_hash(options.root_dir, commit)
    print(short_commit)
    return 0

  @classmethod
  def long_commit(clazz, options, commit):
    check.check_git_cli_options(options)

    long_commit = git.long_hash(options.root_dir, commit)
    print(long_commit)
    return 0
