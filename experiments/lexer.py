#!/usr/bin/env python3

import tomllib
import pprint
import os.path as path

from bes.text.tree_text_parser import tree_text_parser

here = path.dirname(__file__)
keyval_filename = path.join(here, 'keyval.lexer')

with open(keyval_filename, 'r') as f:
  keyval_content = f.read()

tree = tree_text_parser.parse(keyval_content, strip_comments = True, root_name = 'lexer')
#keyval_dict = tomllib.loads(keyval_content)
print(tree)


