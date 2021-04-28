#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#
class dim_system(object):
  'System constants.'

  SYSTEM_NAMES = (
    'alpine',
    'centos',
    'fedora',
    'ubuntu',
  )

  SYSTEM_VERSIONS = {
    'alpine': ( '3.10', '3.12' ),
    'centos': ( '7', '8' ),
    'fedora': ( '29', '30', '32' ),
    'ubuntu': ( '14', '18', '20', ),
  }

  VERSIONED_SYSTEMS = (
    'alpine-3.10',
    'alpine-3.12',
    'centos-7',
    'fedora-29',
    'fedora-30',
    'ubuntu-14',
    'ubuntu-18',
    'ubuntu-20',
  )

  EXPERIMENTAL_VERSIONED_SYSTEMS = (
    'centos-8',
    'fedora-32',
  )

  OLD_SYSTEMS = (
    'alpine-3.10',
    'fedora-29',
    'fedora-30',
    'ubuntu-14',
    'ubuntu-18',
  )

  NEW_SYSTEMS = (
    'alpine-3.12',
    'ubuntu-20',
  )
  
  ALL_VERSIONED_SYSTEMS = tuple(sorted(VERSIONED_SYSTEMS + EXPERIMENTAL_VERSIONED_SYSTEMS))

  DEFAULT_SYSTEMS = tuple(set(VERSIONED_SYSTEMS) - set(EXPERIMENTAL_VERSIONED_SYSTEMS))
  
  CLI_CHOICES = ALL_VERSIONED_SYSTEMS + SYSTEM_NAMES + ( 'all', 'exp', 'allexp', 'old', 'new' )
  
  @classmethod
  def system_name_is_valid(clazz, system_name):
    return system_name in clazz.SYSTEM_NAMES

  @classmethod
  def check_system_name(clazz, system_name):
    if not clazz.system_name_is_valid(system_name):
      raise ValueError('Invalid system_name: "{}" - should be one of {}'.format(system_name, ' '.join(clazz.SYSTEM_NAMES)))
    return system_name

  @classmethod
  def system_version_is_valid(clazz, system_name, system_version):
    clazz.check_system_name(system_name)
    
    return system_version in clazz.SYSTEM_VERSIONS[system_name]

  @classmethod
  def check_system_version(clazz, system_name, system_version):
    clazz.check_system_name(system_name)

    if not system_version in clazz.SYSTEM_VERSIONS[system_name]:
      raise ValueError('Invalid system_version: "{}" - should be one of {}'.format(system_version, ' '.join(clazz.SYSTEM_VERSIONS)))
    return system_version

  @classmethod
  def resolve_systems(clazz, systems):
    if not systems:
      return clazz.DEFAULT_SYSTEMS
    result = []
    for system in systems:
      if system == 'all':
        result.extend(clazz.VERSIONED_SYSTEMS)
      elif system == 'exp':
        result.extend(clazz.EXPERIMENTAL_VERSIONED_SYSTEMS)
      elif system == 'allexp':
        result.extend(clazz.ALL_VERSIONED_SYSTEMS)
      elif system == 'old':
        result.extend(clazz.OLD_SYSTEMS)
      elif system == 'new':
        result.extend(clazz.NEW_SYSTEMS)
      elif system in clazz.SYSTEM_NAMES:
        for possible_system in clazz.ALL_VERSIONED_SYSTEMS:
          if possible_system.startswith(system):
            result.append(possible_system)
      else:
        result.append(system)
    return tuple(set(result))
  
