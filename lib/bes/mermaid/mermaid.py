#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os
import os.path as path
import io
import pprint
from ..common.point import point
from bes.files.bf_check import bf_check
from bes.files.bf_file_ops import bf_file_ops
from ..system.check import check
from ..system.log import logger
from ..text.lexer_token import lexer_token
from ..text.text_line_parser import text_line_parser
from ..text.white_space import white_space
from ..text.bindent import bindent

class mermaid(object):

  _log = logger('mermaid')
  
