#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.text.text_line_parser import text_line_parser

class bat_docker_util(object):
  'Misc docker helper stuff.'
  
  @classmethod
  def parse_lines(clazz, s):
    return text_line_parser.parse_lines(s, strip_comments = False, strip_text = True, remove_empties = True)

  @classmethod
  def make_tagged_image_name(clazz, image_repo, image_tag):
    'Make an image name with an optional tag that can be None'
    check.check_string(image_repo)
    check.check_string(image_tag, allow_none = True)
    
    if image_tag:
      tagged_image = '{}:{}'.format(image_repo, image_tag)
    else:
      tagged_image = image_repo
    return tagged_image
