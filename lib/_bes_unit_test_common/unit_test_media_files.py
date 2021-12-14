#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.property.cached_property import cached_property

from .unit_test_media import unit_test_media

class unit_test_media_files(object):

  @cached_property
  def png_file(self):
    return self.make_temp_file(content = unit_test_media.PNG_SMALLEST_POSSIBLE, suffix = '.png')
  
  @cached_property
  def png_file_wrong_extension(self):
    return self.make_temp_file(content = unit_test_media.PNG_SMALLEST_POSSIBLE, suffix = '.txt')

  @cached_property
  def jpg_file(self):
    return self.make_temp_file(content = unit_test_media.JPG_SMALLEST_POSSIBLE, suffix = '.jpg')
  
  @cached_property
  def jpg_file_wrong_extension(self):
    return self.make_temp_file(content = unit_test_media.JPG_SMALLEST_POSSIBLE, suffix = '.txt')

  @cached_property
  def mp4_file(self):
    return self.make_temp_file(content = unit_test_media.MP4_SMALLEST_POSSIBLE, suffix = '.mp4')
  
  @cached_property
  def mp4_file_wrong_extension(self):
    return self.make_temp_file(content = unit_test_media.MP4_SMALLEST_POSSIBLE, suffix = '.txt')
