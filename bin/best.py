#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

def best_main():
  import sys
  sys.dont_write_bytecode = True
  from bes.tool.tool_cli import tool_cli
  tool_cli.run()

if __name__ == '__main__':
  best_main()
