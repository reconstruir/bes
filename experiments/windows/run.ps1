echo start

$script='c:\Users\build\proj\bes\lib\bes\windows\foo.ps1'
$log_stdout='c:\Users\build\proj\bes\lib\bes\windows\stdout.log'
$log_stderr='c:\Users\build\proj\bes\lib\bes\windows\stderr.log'

$process_options = @{
  FilePath = $script
  RedirectStandardOutput = $log_stdout
  RedirectStandardError = $log_stderr
  UseNewEnvironment = $true
}
#Start-Process @process_options
Start-Process -FilePath "powershell"


# Start-Process -FilePath 'c:\Users\build\proj\bes\lib\bes\windows\foo.ps1' -Verb RunAs
echo done
Exit 0
#  RedirectStandardInput = "stdout.txt"
