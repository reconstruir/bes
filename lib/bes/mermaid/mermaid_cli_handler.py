#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.Script import Script
from ..system.check import check
from bes.fs.file_util import file_util
from bes.fs.file_check import file_check
from bes.script.blurber import blurber

from .mermaid import mermaid
from .mermaid_options import mermaid_options
from .mermaid_ink import mermaid_ink

class mermaid_cli_handler(cli_command_handler):
  'mermaid cli handler.'

  def __init__(self, cli_args):
    super().__init__(cli_args, options_class = mermaid_options)
    
    check.check_mermaid_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)

  def generate(self, filename, namespace, name, output_directory):
    filename = file_check.check_file(filename)
    check.check_string(namespace)
    check.check_string(name)
    check.check_string(output_directory)

    mermaid.state_diagram_generate_code(filename, namespace, name, output_directory)
    
    return 0

  def make(self, filename, output_filename, output_format):
    filename = file_check.check_file(filename)
    check.check_string(output_filename)
    check.check_string(output_format)

    mmd_content = file_util.read(filename, codec = 'utf-8')
    output_bytes = mermaid_ink.img_request(mmd_content, output_format)
    with open(output_filename, 'wb') as f:
      f.write(output_bytes)
    return 0
