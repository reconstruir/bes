#!/bin/bash

PYTHONPATH=$(pwd)/lib uv run pytest ${1+"$@"}
