#!/bin/bash
PROJ="chrome kernel firefox php postgres ffmpeg wireshark tcpdump httpd openssl qemu"
num_procs=$(grep -c ^processor /proc/cpuinfo)
for r in $PROJ
do
   echo "Starting the heuristic on project $r"
   time python ./lifetimes_estimation_parallel.py -p -he=vuldigger2 --delimiter=, $r -pc $num_procs > $r.out 2>&1 &
   sleep 1m
   value=$(cat /proc/loadavg | cut -f1 -d' ')
   while (( $(echo "$value > $num_procs*0.8" |bc -l) ));
   do
	   sleep 1m
	   value=$(cat /proc/loadavg | cut -f1 -d' ')

   done
done
wait
