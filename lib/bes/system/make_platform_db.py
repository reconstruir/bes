#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, json, os, os.path as path, sys

from bes.common import json_util, string_util
from bes.text import text_line_parser as TLP
from bes.fs import file_util
from bes.system import host_info

def main():

  ap = argparse.ArgumentParser()
  ap.add_argument('filename', type = str, action = 'store', help = 'The platforms.txt file.')
  ap.add_argument('output', type = str, action = 'store', help = 'The platforms.txt file.')
  args = ap.parse_args()
  content = file_util.read(args.filename)
  parser = TLP(content)
  lines = TLP.parse_lines(content, strip_comments = True, strip_text = True, remove_empties = True)
  infos = parse_host_infos(lines)

  s = make_host_info_python_list(infos)
  file_util.save(args.output, content = s)
  
#    j = json_util.to_json(infos, indent = 2)
#  for info in infos:
#    print(host_info_to_python_str(info))
#  print(j)

  return 0

def parse_line(s):
  fields = string_util.split_by_white_space(s, strip = True)
  archs = fields[2].split(',')
  fields[2] = tuple(fields[2].split(','))
  return host_info(*fields)

def parse_host_infos(lines):
  return [ parse_line(line) for line in lines ]

#system, version, arch, distro, family, distributor, codename
def host_info_to_python_str(h):
  template = "host_info('{system}', '{version}', {arch}, '{distro}', '{family}', '{distributor}', '{codename}')"
  return template.format(system = h.system,
                         version = h.version,
                         arch = h.arch,
                         distro = h.distro,
                         family = h.family,
                         distributor = h.distributor,
                         codename = h.codename)

def make_host_info_python_list(infos):
  template = """#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
PLATFORMS = [
  {lines}
]"""
  lines = [ host_info_to_python_str(info) for info in infos ]
  return template.format(lines = '\n  '.join(lines))

if __name__ == '__main__':
  raise SystemExit(main())
