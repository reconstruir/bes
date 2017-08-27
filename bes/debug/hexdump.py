#!/usr/bin/env python
#-*- coding:utf-8 -*-

import binascii
from StringIO import StringIO

def hexdump_stream(stream, wordsize = 4, columns = 8, delimiter = ' '):
  'hexdump a stream to a string.'
  v = []
  i = 0
  for chunk in iter(lambda: stream.read(wordsize), b''):
#    print "   chunk: '%s'" % (chunk)
#    print "hexified: '%s'" % (binascii.hexlify(chunk))
    v.append(binascii.hexlify(chunk))
    i += 1
    if (i % columns) == 0:
      v.append('\n')
  s = delimiter + delimiter.join(v)
  lines = s.split('\n')
  return '\n'.join([ line[1:] for line in lines ])

def hexdump(filename, wordsize = 4, columns = 8, delimiter = ' '):
  'hexdump a file to a string.'
  with open(filename, 'rb') as stream:
    return hexdump_fd(stream, wordsize, columns, delimiter)

def hexdump_data(data, wordsize = 4, columns = 8, delimiter = ' '):
  'hexdump a file to a string.'
  return hexdump_stream(StringIO(data), wordsize, columns, delimiter)

  
