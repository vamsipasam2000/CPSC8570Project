#!/bin/bash
cd /srv/vcc_repos/
wget https://archive.org/download/git-history-of-linux/full-history-linux.git.tar
tar -xvf full-history-linux.git.tar
mv history-torvalds linux
cd linux/
git replace --convert-graft-file
git pull
