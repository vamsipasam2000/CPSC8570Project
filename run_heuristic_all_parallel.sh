#!/bin/bash
PROJ="firefox chrome kernel php postgres ffmpeg wireshark tcpdump httpd openssl qemu"
num_procs=$(grep -c ^processor /proc/cpuinfo)
for r in $PROJ
do
   echo "Starting the heuristic on project $r"
#   time python ./lifetimes_estimation_parallel.py -p -he=vuldigger2 --delimiter=, $r -pc $num_procs > $r.out 2>&1 &
   time python ./lifetimes_estimation_parallel.py -p -he=vuldigger2 --delimiter=, $r -pc $num_procs &
   echo "Started heuristic"
   sleep 5m
   value=$(cat /proc/loadavg | cut -f1 -d' ')
   echo $value
   echo $num_procs
   while (( $(echo "$value > $num_procs*0.8" |bc -l) ));
   do
	   sleep 1m
	   value=$(cat /proc/loadavg | cut -f1 -d' ')
   done
done
wait