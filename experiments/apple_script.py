
from os import path

from bes.system.execute import execute
from bes.system.log import logger

import subprocess
subprocess.run(
            ["osascript", "-e", 'tell app "Finder" to empty'],
            capture_output=True,  # Captures stdout and stderr
            text=True  # Returns output as strings instead of bytes
        )
