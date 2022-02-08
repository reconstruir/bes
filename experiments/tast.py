#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import ast

from bes.fs.file_util import file_util

filename = path.join(path.dirname(__file__), 'code.py')

source_code = file_util.read(filename, codec = 'utf-8')

#print(source_code)

tree = ast.parse(source_code)
#print(f'tree={tree}')

#ast.ClassDef

def print_children(node, depth):
  spaces = ' ' * depth
  for child in ast.iter_child_nodes(node):
    print(f'{spaces}{child}')
    if isinstance(child, ast.FunctionDef):
      print(f'{spaces}  func: {child.name} __class__={child.__class__}')
      
#    for x in dir(child):
#      print(f'{spaces}  X: {x}')
#      #return
    #segment = ast.get_source_segment(source_code, child)
    if hasattr(child, 'lineno'):
      if isinstance(child, ast.FunctionDef):
        line_number = child.lineno
        name = child.name
        print(f'  function - {name} {line_number}')
  for child in ast.iter_child_nodes(node):
    print_children(child, depth + 4)

print_children(tree, 0)
