REPOS="https://github.com/mozilla/gecko-dev.git https://github.com/chromium/chromium.git"
for r in $REPOS
do
   echo "Installing repository $r"
   cd /srv/vcc_repos
   git clone "$p"
done
