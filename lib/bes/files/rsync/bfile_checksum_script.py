#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib
import os
import sys

def main():
  if len(sys.argv) < 2:
    print('usage: bfile-checksum.py <file> [algorithm]', file=sys.stderr)
    sys.exit(1)

  filepath = sys.argv[1]
  algorithm = sys.argv[2] if len(sys.argv) > 2 else 'sha256'
  label = algorithm

  if not os.path.exists(filepath):
    print(f'{label}: MISSING')
    sys.stdout.flush()
    return

  total_bytes = os.path.getsize(filepath)
  chunk_size = max(total_bytes // 100, 1048576)
  hasher = hashlib.new(algorithm)
  bytes_done = 0

  with open(filepath, 'rb') as f:
    while True:
      chunk = f.read(chunk_size)
      if not chunk:
        break
      hasher.update(chunk)
      bytes_done += len(chunk)
      print(f'{label}: PROGRESS: {bytes_done}/{total_bytes}')
      sys.stdout.flush()

  print(f'{label}: CHECKSUM: {hasher.hexdigest()}')
  sys.stdout.flush()

if __name__ == '__main__':
  main()
