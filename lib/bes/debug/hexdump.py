#!/usr/bin/env python
#-*- coding:utf-8 -*-

import binascii

def hexdump(filename, wordsize = 4, columns = 8, delimiter = ' '):
  'hexdump a file to a string.'
  v = []
  i = 0
  with open(filename, 'rb') as fin:
    for chunk in iter(lambda: fin.read(wordsize), b''):
      v.append(binascii.hexlify(chunk))
      i += 1
      if (i % columns) == 0:
        v.append('\n')
  s = delimiter + delimiter.join(v)
  lines = s.split('\n')
  return '\n'.join([ line[1:] for line in lines ])
