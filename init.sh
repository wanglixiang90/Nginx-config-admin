cp  config/nginx.sh /etc/init.d/nginx
chmod 755 /etc/init.d/nginx
mkdir -p /etc/nginx/sites-enabled /etc/nginx/sites-available
pip install -r requires.txt