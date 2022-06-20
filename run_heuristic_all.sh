#!/bin/bash
PROJ="chrome postgres mongodb ffmpeg wireshark tcpdump httpd openssl qemu php"
for r in $PROJ
do
   echo "Running the heuristic on project $r"
   time python ./lifetime_estimation.py -p -he=vuldigger2 --delimiter=, $r > $r.out &
done
wait