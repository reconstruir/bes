#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

def best_main():
  import sys
  sys.dont_write_bytecode = True
  from bes.best_cli.best_cli import best_cli
  best_cli.run()

if __name__ == '__main__':
  best_main()
