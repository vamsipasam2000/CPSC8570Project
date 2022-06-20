#!/bin/bash
cd ../cve-search
# We need to patch a small bug we found in cve-search
sed -i 's/thread_map(self.download_site, sites, desc="Downloading files")/thread_map(self.download_site, sites, desc="Downloading files", max_workers=10)/g' ./lib/DownloadHandler.py
./sbin/db_mgmt_cpe_dictionary.py -p
./sbin/db_mgmt_json.py -p
./sbin/db_updater.py -c # This will take >45minutes on a decent machine, please be patient
