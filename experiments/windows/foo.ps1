$log='c:\tmp\fuck.txt'

if (Test-Path -Path $log -PathType Leaf) {
  echo deleting $log
  del $log
}
echo USER=$Env:USER > $log
echo wrote $log
