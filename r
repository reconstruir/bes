#!/bin/bash

PYTHONPATH=$(pwd)/lib uv run --no-project ${1+"$@"}
