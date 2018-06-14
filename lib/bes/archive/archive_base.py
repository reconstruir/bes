#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from collections import namedtuple

class xarchive_base(with_metaclass(ABCMeta, object)):
  'An archive interface.'

  Item = namedtuple('Item', [ 'filename', 'arcname' ])

  @abstractmethod
  def extract(self, dest_dir, base_dir = None,
              strip_common_ancestor = False, strip_head = None,
              include = None, exclude = None):
    '''
    Extract only some contents.
    
    Args:
      dest_dir: The destiation directory where to extract files to.
      base_dir: A base directory to append to the dest_dir or None (optional)
      strip_common_ancestor: If True and *all* filenames have a common ancestor
        the common ancestor will be stripped from each filename.
      strip_head: If given, this string will be stripped from the head of each filename
      include: Optional list of filenames to explicitly include in the extraction.
      exclude: Optional list of filenames to explicitly exclude in the extraction.

    Returns:
        None
    '''
    raise NotImplementedError()

  @abstractmethod
  def create(self, root_dir, base_dir = None,
             extra_items = None,
             include = None, exclude = None):
    raise NotImplementedError()

class archive_base(with_metaclass(ABCMeta, object)):
  'An archive interface.'

  Item = namedtuple('Item', [ 'filename', 'arcname' ])

  @classmethod
  @abstractmethod
  def file_is_valid(clazz, filename):
    'Return True if filename is a valid file supported by this archive format.'
    raise NotImplementedError()

  @abstractmethod
  def _get_members(self):
    '''
    Return the list of raw file and dir contents in the archive.
    This is usually an expensive operation so users should cache the results.
    '''
    raise NotImplementedError()

  @abstractmethod
  def has_member(self, filename):
    '''
    Return True if filename is part of members.  Note that directories should end in '/'
    '''
    raise NotImplementedError()

  @abstractmethod
  def extract_all(self, dest_dir, base_dir = None,
                  strip_common_ancestor = False, strip_head = None):
    '''
    Extract all contents.
    
    Args:
      dest_dir: The destiation directory where to extract files to.
      base_dir: A base directory to append to the dest_dir or None (optional)
      strip_common_ancestor: If True and *all* filenames have a common ancestor
        the common ancestor will be stripped from each filename.
      strip_head: If given, this string will be stripped from the head of each filename

    Returns:
        None
    '''
    raise NotImplementedError()
  
  @abstractmethod
  def create(self, root_dir, base_dir = None,
             extra_items = None,
             include = None, exclude = None):
    raise NotImplementedError()
