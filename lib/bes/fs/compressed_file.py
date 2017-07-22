#!/usr/bin/env python
#-*- coding:utf-8 -*-

import gzip

class compressed_file(object):

  @classmethod
  def read(clazz, filename):
    'Read a comprssed file into a string.'
    with gzip.open(filename, 'rb') as f:
      return f.read()

  @classmethod
  def uncompress(clazz, filename, output):
    'Uncompress a file to another file.'
    assert filename != output
    with gzip.open(filename, 'rb') as fin:
      with open(output, 'wb') as fout:
        fout.write(fin.read())
