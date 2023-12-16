#!/usr/bin/env python3

import tomllib
import pprint
import os.path as path

here = path.dirname(__file__)
keyval_filename = path.join(here, 'keyval.toml')

with open(keyval_filename, 'r') as f:
  keyval_content = f.read()

keyval_dict = tomllib.loads(keyval_content)
print(pprint.pformat(keyval_dict))

