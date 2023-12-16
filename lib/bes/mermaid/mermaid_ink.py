#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import requests
import base64

from ..fs.file_check import file_check
from ..system.check import check
from ..system.log import logger

from .mermaid_error import mermaid_error

class mermaid_ink(object):

  _log = logger('mermaid')

  _BASE_URL = 'https://mermaid.ink/'
  @classmethod
  def img_request(clazz, mmd_content, output_format):
    check.check_string(mmd_content)
    check.check_string(output_format)

    assert output_format in ( 'svg', 'jpg' )
    utf8_bytes = mmd_content.encode('ascii')
    b64_bytes = base64.b64encode(utf8_bytes)
    b64_str = b64_bytes.decode('ascii')
    img_fragment = 'svg' if output_format == 'svg' else 'img'
    url = f'{clazz._BASE_URL}{img_fragment}/{b64_str}?theme=forest'
    response = requests.get(url)
    if response.status_code != 200:
      raise mermaid_error(f'Failed to get url {url}\n{response.content}')
    return response.content
