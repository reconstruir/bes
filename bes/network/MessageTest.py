#!/usr/bin/env python
#-*- coding:utf-8 -*-

message_id = 1

def make_message(content):
  global message_id
  message = {
    'id': message_id,
    'content': content,
  }
  message_id += 1
  return message

def get_line():
  line = None
  try:
    line = raw_input('cmd> ')
  except KeyboardInterrupt, ex:
    return 'exit'
  except EOFError, ex:
    return 'exit'
  if line:
    line = line.strip()
  return line
