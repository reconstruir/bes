#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs, gzip

class compressed_file(object):

  @classmethod
  def read(clazz, filename, codec = None):
    'Read a comprssed file into a string.'
    with gzip.open(filename, 'rb') as f:
      content = f.read()
      if codec:
        return codecs.decode(content, codec)
      else:
        return content

  @classmethod
  def uncompress(clazz, filename, output):
    'Uncompress a file to another file.'
    assert filename != output
    with gzip.open(filename, 'rb') as fin:
      with open(output, 'wb') as fout:
        fout.write(fin.read())
