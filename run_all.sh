#/bin/bash
################################################################################
# First initialize databases
service mysql start
service redis-server start
mongod --config /etc/mongod.conf &
mysql -p123 < ./Database/Scripts/100_combined.sql
################################################################################
# Populate the cve database using the cve-search program
./get_cves.sh
################################################################################
# Clone the repositories to the expected directories, including the full history
# of the Linux kernel.
# This process may take some minutes based on the available bandwidth.
./clone_repos.sh
./get_Linux_full.sh
################################################################################
# Get the mappings between CVEs and fixing commits using the available methods
./get_mappings_all.sh
################################################################################
# Run the heuristic to estimate the lifetime of vulnerabilities
# This is a parallel version of the heuristic, however there are still major
# sequestian parts and the parallelization can be improved in the future.
# This step can require many hours
./run_heuristic_all_parallel.sh
################################################################################
# Just copy the output to the expected location for the analysis scripts and
# prepare the directories where the results and plots will be saved.
./copy_output.sh
./create_out_dirs.sh
################################################################################
# Run the preprocessing and Analysis scripts that will produce the results.
cd ./Analysis
python preprocessing.py
python HeuristicEval.py
python Analysis.py
