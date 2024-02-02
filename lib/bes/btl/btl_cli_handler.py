#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import os.path as path

from ..cli.cli_command_handler import cli_command_handler
from ..common.Script import Script
from ..fs.file_check import file_check
from ..fs.file_util import file_util
from ..fs.temp_file import temp_file
from ..script.blurber import blurber
from ..system.check import check
from ..files.bf_filename import bf_filename

from ..btl.btl_lexer_desc import btl_lexer_desc
from ..mermaid.mermaid_ink import mermaid_ink

from .btl_cli_options import btl_cli_options

class btl_cli_handler(cli_command_handler):
  'btl cli handler.'

  def __init__(self, cli_args):
    super().__init__(cli_args, options_class = btl_cli_options)
    
    check.check_btl_cli_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)

  def lexer_make_mmd(self, filename, output_filename):
    filename = file_check.check_file(filename)
    check.check_string(output_filename)

    desc = btl_lexer_desc.parse_file(filename)
    with open(output_filename, 'w') as f:
      f.write(desc.to_mermaid_diagram())
    return 0
  
  def lexer_make_diagram(self, filename, output_filename, output_format):
    filename = file_check.check_file(filename)
    check.check_string(output_filename)
    check.check_string(output_format)

    desc = btl_lexer_desc.parse_file(filename)
    mmd_content = desc.to_mermaid_diagram()
    output_bytes = mermaid_ink.img_request(mmd_content, output_format)
    with open(output_filename, 'wb') as f:
      f.write(output_bytes)
    return 0
    
  def lexer_make_code(self, filename, output_filename, namespace, name):
    filename = file_check.check_file(filename)
    check.check_string(output_filename)
    check.check_string(namespace, allow_none = True)
    check.check_string(name, allow_none = True)

    parsed_namespace, parsed_name = self._parse_code_filename(output_filename)
    namespace = namespace or parsed_namespace
    name = name or parsed_name
    desc = btl_lexer_desc.parse_file(filename)
    desc.write_code(output_filename, namespace, name)
    return 0

  _parsed_code_filename = namedtuple('_parsed_code_filename', 'namespace, name')
  @classmethod
  def _parse_code_filename(clazz, filename):
    basename = bf_filename.without_extension(path.basename(filename))

    has_underscore = basename.startswith('_')

    if has_underscore:
      basename = basename[1:]
    parts = basename.split('_')
    namespace = parts.pop(0)
    name = '_'.join(parts)
    if has_underscore:
      namespace = '_' + namespace
    return clazz._parsed_code_filename(namespace, name)
