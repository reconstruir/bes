#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.files.bf_check import bf_check
from bes.files.bf_file_ops import bf_file_ops
from bes.system.check import check

from .mermaid import mermaid
from .mermaid_ink import mermaid_ink

class mermaid_command_handler(bcli_command_handler):

  def name(self):
    return 'mermaid'

  def _command_generate(self, filename, namespace, name, output_directory, options):
    filename = bf_check.check_file(filename)
    check.check_string(namespace)
    check.check_string(name)
    check.check_string(output_directory)

    mermaid.state_diagram_generate_code(filename, namespace, name, output_directory)
    return 0

  def _command_make(self, filename, output_filename, output_format, options):
    filename = bf_check.check_file(filename)
    check.check_string(output_filename)
    check.check_string(output_format)

    mmd_content = bf_file_ops.read(filename, encoding='utf-8')
    output_bytes = mermaid_ink.img_request(mmd_content, output_format)
    with open(output_filename, 'wb') as f:
      f.write(output_bytes)
    return 0
