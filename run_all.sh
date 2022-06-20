#/bin/bash
service mysql start
service redis-server start
mongod --config /etc/mongod.conf &
mysql -p < ./Database/Scripts/100_combined.sql
./get_cves.sh
./clone_repos.sh
./get_Linux_full.sh
./get_mappings_all.sh
./run_heuristic_all_parallel.sh
./copy_output.sh
./create_out_dirs.sh
cd ./Analysis
python preprocessing.py
python Analysis.py
