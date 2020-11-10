#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs, gzip

from .file_util import file_util

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
    'Uncompress a gzipped file to another file.'
    assert filename != output

    file_util.ensure_file_dir(output)

    with gzip.open(filename, 'rb') as fin:
      with open(output, 'wb') as fout:
        fout.write(fin.read())

  @classmethod
  def compress(clazz, filename, output):
    'Compress a file to another file with gzip.'
    assert filename != output

    file_util.ensure_file_dir(output)
    
    with open(filename, 'rb') as fin:
      with gzip.open(output, 'wb') as fout:
        fout.write(fin.read())
