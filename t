#!/bin/bash

PYTHONPATH=lib uv run pytest ${1+"$@"}
