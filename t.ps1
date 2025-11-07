# Set the PYTHONPATH environment variable
$env:PYTHONPATH = "..\bes\lib;lib"

# Run pytest with any arguments passed to this script
uv run pytest @args
