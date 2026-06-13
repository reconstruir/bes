#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.files.bf_check import bf_check
from bes.system.check import check

from .bat_project import bat_project
from .bat_project_options import bat_project_options

class bat_project_command_handler(bcli_command_handler):

  def name(self):
    return 'bat_project'

  def _make_project(self, options):
    return bat_project(options=bat_project_options(
      verbose=options.verbose,
      debug=options.debug,
      root_dir=options.root_dir,
      name=options.name,
      uv_exe=options.uv_exe,
    ))

  def _command_activate_script(self, version, variant, options):
    check.check_string(variant, allow_none=True)
    check.check_string(version)

    project = self._make_project(options)
    script = project.activate_script(version, variant=variant)
    print(script)
    return 0

  def _command_ensure(self, versions, requirements, requirements_dev, options):
    check.check_string_seq(versions)
    requirements = bf_check.check_file(requirements)
    requirements_dev = bf_check.check_file(requirements_dev, allow_none=True)

    project = self._make_project(options)
    project.ensure(versions, requirements, requirements_dev=requirements_dev)
    return 0
