PROJ="firefox chrome kernel postgres ffmpeg wireshark tcpdump httpd openssl qemu php"
for r in $PROJ
do
   echo "Getting mappings for  project $r"
#   time python vcc_mapper.py -d $r > ./out/mappings_log_$r.out 2>&1
   time python vcc_mapper.py -d $r
done
wget -O ./Data/ThirdPartyMappings/kernel_cves.json https://raw.githubusercontent.com/nluedtke/linux_kernel_cves/master/data/kernel_cves.json
python ./Scripts/ThirdPartyMappings/import_debian_security_mappings.py
python ./Scripts/ThirdPartyMappings/import_kernel_cves.py
python ./Scripts/ThirdPartyMappings/import_httpd_piantadosi.py
