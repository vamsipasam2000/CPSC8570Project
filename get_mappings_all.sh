PROJ="firefox chrome kernel postgres ffmpeg wireshark tcpdump httpd openssl qemu php"
for r in $PROJ
do
   echo "Getting mappings for  project $r"
   time python vcc_mapper.py -d $r > ./out/mappings_log_$r.out 2>&1
done
