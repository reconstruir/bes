#!/bin/bash

_s=~/tmp/caca/bes/bin/best.sh

${_s} refactor rename 'from bes.fs.file_check import file_check' 'from bes.files.bf_check import bf_check' $(ag bes.fs.file_check -l)

${_s} refactor rename 'file_check.check_file' 'bf_check.check_file' $(ag file_check.check_file -l)

${_s} refactor rename 'file_check.check_dir' 'bf_check.check_dir' $(ag file_check.check_dir -l)

