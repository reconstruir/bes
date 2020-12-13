#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path, getcwd

from bes.common.check import check
from bes.common.string_util import string_util
from bes.common.table import table
from bes.system.command_line import command_line
from bes.fs.file_util import file_util
from bes.git.git import git
from bes.git.git_util import git_util
from bes.text.text_table import text_cell_renderer
from bes.text.text_table import text_table
from bes.text.text_table import text_table_style
from bes.text.text_box import text_box_colon
from bes.text.text_box import text_box_unicode
from bes.version.software_version import software_version

from bes.git.git_repo_document_db import git_repo_document_db

from .git_cli_util import git_cli_util

class git_cli_command(object):

  DEFAULT_NAME = 'bitbckt-org-wm-bldr'
  DEFAULT_EMAIL = 'noreply@imvu.com'
  
  @classmethod
  def set_identity(clazz, name, email):
    check.check_string(name)
    check.check_string(email)
    git.config_set_identity(name, email)
    return 0

  @classmethod
  def get_identity(clazz, name, email):
    check.check_bool(name)
    check.check_bool(email)
    identity = git.config_get_identity()
    if name:
      print(identity.name)
    elif email:
      print(identity.email)
    else:
      if identity.name and identity.email:
        print('{name}:{email}'.format(name = identity.name, email = identity.email))
      elif identity.name:
        print(identity.name)
      elif identity.email:
        print(identity.email)
      else:
        print('')
    return 0
  
  @classmethod
  def ensure_identity(clazz):
    identity = git.config_get_identity()
    if not identity.name or not identity.email:
      clazz.set_identity(clazz.DEFAULT_NAME, clazz.DEFAULT_EMAIL)
    return 0
      
  _DELTA_MAP = {
    'major': [ 1, 0, 0 ],
    'minor': [ 0, 1, 0 ],
    'revision': [ 0, 0, 1 ],
  }
  
  @classmethod
  def bump_tag(clazz, root_dir, component, dry_run, dont_push, reset_lower, verbose):
    old_tag = git.greatest_local_tag(root_dir)
    bump_rv = git.bump_tag(root_dir, component, push = not dont_push, dry_run = dry_run, reset_lower = reset_lower)
    blurb = 'old_tag={} new_tag={}'.format(bump_rv.old_tag, bump_rv.new_tag)
    if dry_run:
      print('dry_run: {} dont_push={}'.format(blurb, dont_push))
    if verbose:
      print(blurb)
    return 0

  @classmethod
  def delete_tags(clazz, root_dir, tags, local, remote, dry_run, from_file):
    check.check_string(root_dir)
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
      git.delete_tag(root_dir, tag, where, dry_run)
    return 0
  
  @classmethod
  def list_tags(clazz, root_dir, local, remote):
    check.check_bool(local, allow_none = True)
    check.check_bool(remote, allow_none = True)
    where = git.determine_where(local, remote)
    if where == 'both':
      clazz._list_tags_both(root_dir)
      return 0
    if where == 'local':
      tags = git.list_local_tags(root_dir)
    else:
      tags = git.list_remote_tags(root_dir)
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
  def tag(clazz, root_dir, tag, local, remote, commit):
    check.check_bool(local, allow_none = True)
    check.check_bool(remote, allow_none = True)
    check.check_string(commit, allow_none = True)
    
    where = git.determine_where(local, remote)
    if not tag:
      clazz._tag_print(root_dir, where)
    else:
      clazz._tag_set(root_dir, tag, where, commit)
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
  def retag(clazz, root_dir, tag = None, verbose = False):
    tag = tag or git.greatest_local_tag(root_dir)
    git.delete_tag(root_dir, tag, 'both', False)
    git.tag(root_dir, tag)
    git.push_tag(root_dir, tag)
    if verbose:
      print('old_tag={} new_tag={}'.format(tag, tag))
    return 0

  @classmethod
  def repo_bump_tag(clazz, address, component, dry_run, reset_lower):
    result = git_util.repo_bump_tag(address, component, dry_run, reset_lower)
    if dry_run:
      print('dry_run: old_tag={} new_tag={}'.format(result.old_tag, result.new_tag))
    return 0

  @classmethod
  def repo_greatest_tag(clazz, address):
    greatest_tag = git_util.repo_greatest_tag(address)
    print(greatest_tag)
    return 0

  @classmethod
  def repo_run_scripts(clazz, address, scripts, options):
    v = [ clazz._parse_script(script) for script in scripts ]
    result = git_util.repo_run_scripts(address, v, options = options)
    if options.verbose:
      print('status:\n{}\n'.format(result.status))
      print('  diff:\n{}\n'.format(result.diff))
      for rv in result.results:
        print('{}'.format(rv.script))
        print('{}'.format(rv.stdout))
    return 0

  @classmethod
  def repo_clone(clazz, address, dest_dir, options):
    git.clone(address, dest_dir, options = options) 
    return 0
  
  @classmethod
  def repo_sync(clazz, address, dest_dir, options):
    git.sync(address, dest_dir, options = options) 
    return 0
  
  @classmethod
  def _parse_script(clazz, cmd):
    args = command_line.parse_args(cmd)
    return git_util.script(args[0], args[1:])

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
  def branches(clazz, root_dir, local, remote, brief, plain, difference, no_fetch):
    check.check_bool(local, allow_none = True)
    check.check_bool(remote, allow_none = True)
    check.check_bool(brief)
    check.check_bool(plain)
    check.check_bool(difference)
    check.check_bool(no_fetch)
    where = git.determine_where(local, remote)
    if not no_fetch:
      git.fetch(root_dir)
    branches = git.list_branches(root_dir, where)
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
    title = git.remote_origin_url(root_dir)
    clazz._print_branches(title, branches, branches.longest_name, branches.longest_comment, plain)
    return 0

  @classmethod
  def update_document(clazz, input_filename, address, branch, working_dir, commit_msg):
    # For the purposes of this CLI, the name of the stored file in the repo will be the same as the
    # base name of the file used to provide the source document contents.
    filename = path.basename(input_filename)
    db = git_repo_document_db(working_dir, address, branch)
    new_contents = file_util.read(input_filename)
    if not commit_msg:
      commit_msg = 'git_repo_document_db commit'

    # For the purposes of this CLI, just throw away the old contents. There's no way to update them.
    db.update_document(filename, lambda old_contents: new_contents, commit_msg)

    return 0

  @classmethod
  def load_document(clazz, filename, address, branch, output_filename, working_dir):
    db = git_repo_document_db(working_dir, address, branch)
    if not output_filename:
      output_filename = path.join(getcwd(), filename)
    content = db.load_document(filename)
    file_util.save(output_filename, content)
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
  def short_commit(clazz, root_dir, commit):
    short_commit = git.short_hash(root_dir, commit)
    print(short_commit)
    return 0

  @classmethod
  def long_commit(clazz, root_dir, commit):
    long_commit = git.long_hash(root_dir, commit)
    print(long_commit)
    return 0
  
