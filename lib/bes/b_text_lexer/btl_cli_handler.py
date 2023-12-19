#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from ..cli.cli_command_handler import cli_command_handler
from ..common.Script import Script
from ..fs.file_check import file_check
from ..fs.file_util import file_util
from ..fs.temp_file import temp_file
from ..script.blurber import blurber
from ..system.check import check

from ..b_text_lexer.btl_desc import btl_desc
from ..mermaid.mermaid_ink import mermaid_ink

from .btl_cli_options import btl_cli_options

#from .mermaid import mermaid
#from .mermaid_options import mermaid_options


class btl_cli_handler(cli_command_handler):
  'btl cli handler.'

  def __init__(self, cli_args):
    super().__init__(cli_args, options_class = btl_cli_options)
    
    check.check_btl_cli_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)

  def generate(self, filename, namespace, name, output_directory):
    filename = file_check.check_file(filename)
    check.check_string(namespace)
    check.check_string(name)
    check.check_string(output_directory)

    mermaid.state_diagram_generate_code(filename, namespace, name, output_directory)
    
    return 0

  def make_diagram(self, filename, output_filename, output_format):
    filename = file_check.check_file(filename)
    check.check_string(output_filename)
    check.check_string(output_format)

    tmp = temp_file.make_temp_file(suffix = '.mmd')
    self.make_mmd(filename, tmp)
    mmd_content = file_util.read(tmp, codec = 'utf-8')
    output_bytes = mermaid_ink.img_request(mmd_content, output_format)
    with open(output_filename, 'wb') as f:
      f.write(output_bytes)
    return 0
    
  def make_mmd(self, filename, output_filename):
    filename = file_check.check_file(filename)
    check.check_string(output_filename)

    desc = btl_desc.parse_file(filename)
    with open(output_filename, 'w') as f:
      f.write(desc.to_mermaid_diagram())
    return 0
  
