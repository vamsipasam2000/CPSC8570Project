#!/bin/bash
PROJ="firefox chrome kernel php postgres ffmpeg wireshark tcpdump httpd openssl qemu"
for r in $PROJ
do
	cp ./out/${r}_par.csv ./Data/Lifetimes/${r}.csv
done
