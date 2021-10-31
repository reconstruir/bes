#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class git_cli_common_args(object):

  @classmethod
  def git_cli_add_common_args(clazz, p):
#    p.add_argument('-s', '--style', action = 'store', default = 'table',
#                   dest = 'output_style', choices = ( 'brief', 'json', 'plain', 'table' ),
#                   help = 'Output style. [ table ]')
#    p.add_argument('-o', '--output', action = 'store', default = None,
#                   dest = 'output_filename',
#                   help = 'Write output to filename instead of stdout. [ None ]')
    p.add_argument('--output', action = 'store', default = None,
                   dest = 'output_filename',
                   help = 'Optional output filename [ None ]')
    from bes.data_output.data_output_style import data_output_style
    p.add_argument('--style', action = 'store', default = data_output_style.BRIEF,
                   dest = 'output_style',
                   choices = data_output_style.values,
                   help = 'Output style [ BRIEF ]')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   help = 'Verbose output.  Mostly for the results (git status and diff). [ False ]')
    p.add_argument('--dry-run', action = 'store_true',
                   help = 'Dont do it just print it. [ False ]')
    p.add_argument('--debug', action = 'store_true',
                   help = 'Keep temporary files and dirs for debugging. [ False ]')
