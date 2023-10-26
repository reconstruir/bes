#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#from bes.compat.StringIO import StringIO
#from bes.common.string_util import string_util
#from bes.common.point import point
from bes.system.log import log
#from bes.text.line_break import line_break

#from .bc_ini_lexer_token import bc_ini_lexer_token
#from .bc_ini_lexer_options import bc_ini_lexer_options
#from .bc_ini_error import bc_ini_error

#from ._detail._bc_ini_lexer_state import _bc_ini_lexer_state_begin
#from ._detail._bc_ini_lexer_state import _bc_ini_lexer_state_comment
#from ._detail._bc_ini_lexer_state import _bc_ini_lexer_state_done
#from ._detail._bc_ini_lexer_state import _bc_ini_lexer_state_double_quoted_string
#from ._detail._bc_ini_lexer_state import _bc_ini_lexer_state_single_quoted_string
#from ._detail._bc_ini_lexer_state import _bc_ini_lexer_state_space
#from ._detail._bc_ini_lexer_state import _bc_ini_lexer_state_string

class text_lexer_base(object):

  #EOS = '\0'
  #
  #SINGLE_QUOTE_CHAR = '\''
  #DOUBLE_QUOTE_CHAR = "\""
  #COMMENT_CHAR = ';'

  def __init__(self, log_tag, source = None):
    log.add_logging(self, tag = log_tag)

#    self._options = options or bc_ini_lexer_options.DEFAULT_OPTIONS
    self._source = source or '<unknown>'
#    self._keep_quotes = (self._options & bc_ini_lexer_options.KEEP_QUOTES) != 0
#    self._escape_quotes = (self._options & bc_ini_lexer_options.ESCAPE_QUOTES) != 0
#    self._ignore_comments = (self._options & bc_ini_lexer_options.IGNORE_COMMENTS) != 0
#    self._buffer = None
#    self._is_escaping = False
#    self._last_char = None
    
