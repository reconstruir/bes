#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse
import datetime


def complete(parser_manager, cword, words):
  '''Lightweight dynamic completion — no heavy imports.

  Returns a list of completion candidates for the word at position cword.
  Only completes top-level command names; flags require building the argparse
  parser which triggers heavy imports and is left to the static baked script.

  words is the full COMP_WORDS array including argv[0].
  '''
  if cword <= 0:
    return []

  if cword == 1:
    return parser_manager.children_at([])

  return []


def generate_script(parser_manager, prog_name, wrapper=None):
  '''Build every registered parser and emit a static bash completion script.

  prog_name  — basename of the program (e.g. 'rmusic1.py').
  wrapper    — optional command that wraps the invocation (e.g. './r').
               When provided, a second completion is registered for the
               wrapper command so that typing '<wrapper> <prog_name> <TAB>'
               also works.  The wrapper completion guards on COMP_WORDS[1]
               matching prog_name, so it is safe to register even when the
               wrapper script is used for other purposes.

  This is intentionally slow — heavy factory imports happen here so that
  TAB completion at runtime requires no Python at all.
  '''
  top_level_commands = parser_manager.children_at([])
  completion_data = {}

  for path, factory_class in parser_manager.all_factory_classes():
    if len(path) != 1:
      continue
    cmd = path[0]
    factory_instance = factory_class()

    parser = argparse.ArgumentParser(prog=f'{prog_name} {cmd}', add_help=False)
    factory_instance.add_arguments(parser)

    entry = {'subcommands': [], 'subcommand_flags': {}}

    if factory_instance.has_commands():
      subparsers = parser.add_subparsers(dest='__cmd__')
      factory_instance.add_commands(subparsers)

      for subcmd_name, subcmd_parser in sorted(subparsers.choices.items()):
        entry['subcommands'].append(subcmd_name)
        flags = []
        for action in subcmd_parser._actions:
          flags.extend(action.option_strings)
        entry['subcommand_flags'][subcmd_name] = sorted(flags)

    completion_data[cmd] = entry

  return _render_bash_script(prog_name, wrapper, top_level_commands, completion_data)


def _render_bash_script(prog_name, wrapper, top_level_commands, completion_data):
  func_name = '_' + prog_name.replace('.', '_').replace('-', '_') + '_complete'
  timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  top_level_words = ' '.join(sorted(top_level_commands))

  lines = []
  lines.append(f'# bash completion for {prog_name}')
  lines.append(f'# generated: {timestamp}')
  lines.append(f'# regenerate with: {prog_name} --bcli-generate-completion bash')
  lines.append('')

  # Core impl function — offset controls where commands start in COMP_WORDS.
  # offset=1 for direct invocation: prog_name cmd subcmd
  # offset=2 for wrapper invocation: wrapper prog_name cmd subcmd
  lines.append(f'{func_name}_impl() {{')
  lines.append(f'    local _offset="$1"')
  lines.append(f'    local cur="${{COMP_WORDS[COMP_CWORD]}}"')
  lines.append(f'    local cmd="${{COMP_WORDS[$_offset]}}"')
  lines.append(f'    local subcmd="${{COMP_WORDS[$(( _offset + 1 ))]}}"')
  lines.append(f'    case "$cmd" in')

  for cmd in sorted(completion_data.keys()):
    entry = completion_data[cmd]
    lines.append(f'        {cmd})')
    if entry['subcommand_flags']:
      lines.append(f'            case "$subcmd" in')
      for subcmd in sorted(entry['subcommand_flags'].keys()):
        flags_str = ' '.join(entry['subcommand_flags'][subcmd])
        lines.append(f'                {subcmd})')
        lines.append(f'                    COMPREPLY=($(compgen -W "{flags_str}" -- "$cur"))')
        lines.append(f'                    return ;;')
      lines.append(f'            esac')
    if entry['subcommands']:
      subcmds_str = ' '.join(sorted(entry['subcommands']))
      lines.append(f'            COMPREPLY=($(compgen -W "{subcmds_str}" -- "$cur"))')
    lines.append(f'            return ;;')

  lines.append(f'    esac')
  lines.append(f'    COMPREPLY=($(compgen -W "{top_level_words}" -- "$cur"))')
  lines.append(f'}}')
  lines.append('')

  # Direct invocation: prog_name cmd subcmd  (offset=1)
  lines.append(f'{func_name}() {{')
  lines.append(f'    {func_name}_impl 1')
  lines.append(f'}}')
  lines.append(f'complete -o default -F {func_name} {prog_name}')

  if wrapper:
    # Wrapper invocation: wrapper prog_name cmd subcmd  (offset=2)
    # Guards on COMP_WORDS[1] matching prog_name so the wrapper's normal
    # filename completion still works for any other script it might run.
    wrapper_func = func_name + '_wrapper'
    lines.append('')
    lines.append(f'{wrapper_func}() {{')
    lines.append(f'    [[ "${{COMP_WORDS[1]}}" == *"{prog_name}" ]] || {{ COMPREPLY=(); return 0; }}')
    lines.append(f'    {func_name}_impl 2')
    lines.append(f'}}')
    lines.append(f'complete -o default -F {wrapper_func} {wrapper}')

  return '\n'.join(lines)
