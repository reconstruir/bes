#BTL
#
# Line break lexer
#
lexer
  name: btl_line_break_lexer
  description: A line break lexer
  version: 1.0

tokens
  t_line_break
    type_hint: h_line_break

errors
  e_unexpected_char: In state {state} unexpected character {char}
  e_unexpected_eos: In state {state} unexpected end-of-string

states

  s_line_break
    c_nl: s_start
      buffer write
      yield t_line_break
      buffer reset
    c_nl: s_start
    default: s_done
      raise e_unexpected_eos
