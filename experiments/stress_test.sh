#!/bin/bash

export BES_LOG="vmware=debug vmware_client=debug vmware_server=debug vmware_session=debug vmware_credentials=debug"

mkdir -p logs
rm -rf logs/*

for i in {1..1000}; do
  echo "test $i"
  #best.py vmware vm_set_power poto3 off >& logs/$i.log
  best.py vmware vm_set_power poto3 off >& logs/off_$i.log
  time ( ./do_test.sh lib/bes/text --clone-vm >> logs/$i.log )
  rv=$?
  if [[ $rv != 0 ]]; then
    echo "failed: logs/$i.log"
    exit 1
  fi
done
echo "success: all tests passed"
exit 0
