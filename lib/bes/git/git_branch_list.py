#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.string_util import string_util
from bes.common.type_checked_list import type_checked_list
from bes.data_output.data_output import data_output
from bes.data_output.data_output_options import data_output_options
from bes.data_output.data_output_style import data_output_style
from bes.system.check import check

from bes.text.text_box import text_box_colon
from bes.text.text_box import text_box_unicode
from bes.text.text_table import text_cell_renderer
from bes.text.text_table import text_table
from bes.text.text_table import text_table_style

from .git_branch import git_branch 

class git_branch_list(type_checked_list):

  __value_type__ = git_branch
  
  def __init__(self, values = None):
    super(git_branch_list, self).__init__(values = values)
    
  @property
  def local_names(self):
    return sorted([ b.name for b in self if b.where == 'local' ])
    
  @property
  def remote_names(self):
    return sorted([ b.name for b in self if b.where == 'remote' ])
    
  @property
  def names(self):
    return sorted(list(set(self.local_names + self.remote_names)))

  @property
  def longest_name(self):
    return max([ len(name) for name in self.names ])

  @property
  def comments(self):
    return sorted(list(set([ b.comment for b in self ])))

  @property
  def longest_comment(self):
    return max([ len(comment) for comment in self.comments ])

  @property
  def difference(self):
    'Return remote branches not local.'
    remote_set = set(self.remote_names)
    local_set = set(self.local_names)
    return sorted(list(remote_set - local_set))

  def has_local(self, name):
    return name in self.local_names

  def has_remote(self, name):
    return name in self.remote_names

  def mutated_values(self, mutations):
    return git_branch_list([ v.clone(mutations) for v in self ])
    
  def find_by_name(self, name):
    for b in self:
      if b.name == name:
        return b
    return None

  def output(self, style, output_filename = None, table_title = None):
    style = check.check_data_output_style(style)
    check.check_string(output_filename, allow_none = True)
    check.check_string(table_title, allow_none = True)
    
    from bes.system.console import console
    from bes.system.log import log

    try:
      width = console.terminal_width()
    except Exception as ex:
      width = None

    #log.console('width={}'.format(width))
      
    r = { 'AHEAD': 'AH', 'BEHIND': 'BE', 'ACTIVE': '*' }
    table_labels = tuple([ string_util.replace(f.upper(), r) for f in self._values[0]._fields ])
    longest_comment = 60 # self.longest_comment
    table_cell_renderers = {
      '*': self._branch_active_cell_renderer(),
      'AH': self._branch_ahead_behind_cell_renderer(),
      'BE': self._branch_ahead_behind_cell_renderer(),
      'NAME': text_cell_renderer(width = self.longest_name),
      'COMMENT': text_cell_renderer(width = longest_comment),
    }
    options = data_output_options(brief_column = 0,
                                  output_filename = output_filename,
                                  style = style,
                                  table_labels = table_labels,
                                  table_cell_renderers = table_cell_renderers,
                                  table_title = table_title)
    data_output.output_table(self._values, options = options)
  
  class _branch_active_cell_renderer(text_cell_renderer):

    def __init__(self, *args, **kargs):
      text_cell_renderer.__init__(self, *args, **kargs)
      
    def render(self, value, width = None, is_label = False):
      if is_label:
        return value
      return '*' if value else ' '

  class _branch_ahead_behind_cell_renderer(text_cell_renderer):

    def __init__(self, *args, **kargs):
      text_cell_renderer.__init__(self, *args, **kargs)

    def render(self, value, width = None, is_label = False):
      if is_label:
        return value
      return str(value).center(2) if value else ' ' * 2
    
