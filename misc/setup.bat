@echo off
set PYTHONPATH=%~dp0\..\lib;%PYTHONPATH%
set PATH=%~dp0\..\bin;%PATH%
set VISUAL=emacs

rem set PROMPT="$E[m$E[32m$E]9;8;\"USERNAME\"$E\@$E]9;8;\"COMPUTERNAME\"$E\$S$E[92m$P$E[90m$_$E[90m$$$E[m$S$E]9;12$E\"
rem GitShowBranch /i


rem $P$E]9;7;"cmd -cur_console:R /cGitShowBranch.cmd"$e\$E]9;8;"gitbranch"$e\$g
rem $E[m$E[32m$E]9;8;"USERNAME"$E\@$E]9;8;"COMPUTERNAME"$E\$S$E[92m$P$E[90m$_$E[90m$$$E[m$S$E]9;12$E\
