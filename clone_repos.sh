REPOS="https://github.com/mozilla/gecko-dev.git https://github.com/chromium/chromium.git https://github.com/postgres/postgres.git https://github.com/WordPress/wordpress-develop.git https://github.com/FFmpeg/FFmpeg.git https://github.com/wireshark/wireshark.git https://github.com/the-tcpdump-group/tcpdump.git https://github.com/jp-wagner/httpd.git https://github.com/openssl/openssl.git https://github.com/php/php-src.git https://github.com/qemu/qemu.git"
mkdir /srv/vcc_repos
for r in $REPOS
do
   echo "Cloning repository $r"
   cd /srv/vcc_repos
   echo "$r"
   git clone "$r"
done
