#!/bin/bash

PYTHONPATH=$(pwd)/lib uv run ${1+"$@"}
