#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#

from bes.property.cached_property import cached_property
from bes.dependency.dependency_resolver import dependency_resolver

from .dim_artifact_descriptor import dim_artifact_descriptor

class dim_artifact_manager(object):
    
  def __init__(self, script, artifacts_config, python_version, system_name, system_version, required_artifacts):
    self.script = script
    self.config = artifacts_config
    self.required_artifacts = required_artifacts

    # Remove all the python sections except the one we want by version
    # but rename it from python-x.y to just python to siplify that logic
    # elsewhere in this script
    old_values = self.config.section('python-{}'.format(python_version)).to_key_value_list()
    to_remove = []
    for section in self.config:
      if section.header_.name.startswith('python'):
        to_remove.append(section.header_.name)
    for section_name in to_remove:
      self.config.remove_section(section_name)
    new_section = self.config.add_section('python')
    new_section.set_values(old_values)
      
    self.system_name = system_name
    self.system_version = system_version
    self.artifacts = self._parse_artifacts()

  def __getitem__(self, key):
    return self.artifacts[key]

  @cached_property
  def dep_map(self):
    dep_map = {}
    for name, artifact in self.artifacts.items():
      dep_map[name] = set(artifact.depends)
    return dep_map

  @cached_property
  def build_order(self):
    dep_map = self.dep_map
    build_order = dependency_resolver.build_order_flat(dep_map)
    build_order = [ name for name in build_order if name in self.required_artifacts ]
    return build_order
    
  def _parse_artifacts(self):
    artifacts = {}
    for section in self.config:
      build_script = self.script._helper.find_artifact_build_script('steps/base/artifact_build_scripts',
                                                                    section.header_.name,
                                                                    self.system_name,
                                                                    self.system_version,
                                                                    raise_error = False)
      artifact = dim_artifact_descriptor(section,
                                         self.system_name,
                                         self.system_version,
                                         build_script,
                                         self.script._helper.build_dir)
      if artifact.name in artifacts:
        raise RuntimeError('Duplicate artifact: {}'.format(artifact.name))
      artifacts[artifact.name] = artifact
    return artifacts
