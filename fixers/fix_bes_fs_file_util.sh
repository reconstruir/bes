#!/bin/bash

_s=~/tmp/caca/bes/bin/best.sh

${_s} refactor rename 'from bes.fs.file_util import file_util' 'from bes.files.bf_file_ops import bf_file_ops' $(ag bes.fs.file_util -l)

${_s} refactor rename 'from .file_util import file_util' 'from bes.files.bf_file_ops import bf_file_ops' $(ag 'from .file_util import file_util' -l)

${_s} refactor rename 'from ..fs.file_util import file_util' 'from bes.files.bf_file_ops import bf_file_ops' $(ag 'from ..fs.file_util import file_util' -l)

${_s} refactor rename 'file_util.' 'bf_file_ops.' $(ag file_util. -l)
