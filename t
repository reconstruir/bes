#!/bin/bash

PYTHONPATH=../bes/lib:lib uv run pytest ${1+"$@"}
