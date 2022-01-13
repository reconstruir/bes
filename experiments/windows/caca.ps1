#Powershell -Command "& { Start-Process \"C:\Users\build\proj\bes\python-3.7.8-amd64.exe /quiet InstallAllUsers=1 PrependPath=1\" }" -Verb RunAs

write-host "hello"

$git = "C:\Program Files\Git\cmd\git.exe"
write-host "$git"
$arguments = "status"
write-host start-process $git $arguments


$rv=main $Args
exit $rv
