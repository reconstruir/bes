#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

if __name__ == '__main__':
  from bes.docker_image_maker.dim_build_cli import dim_build_cli
  from os import path
  root_dir = path.abspath(path.join(path.dirname(__file__), '..'))
  raise SystemExit(dim_build_cli.main(root_dir))
