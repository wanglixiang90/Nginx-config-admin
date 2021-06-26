
yum -y install nginx
yum -y install python3 python3-pip

cp  config/nginx.sh /etc/init.d/nginx
chmod 755 /etc/init.d/nginx
mkdir -p /etc/nginx/sites-enabled /etc/nginx/sites-available
[ -f /etc/nginx/nginx.conf ] && mv /etc/nginx/nginx.conf{,-$(date +%s)}
\cp config/nginx.conf  /etc/nginx/nginx.conf

pip3 install --upgrade pip
pip3 install -r requires.txt

sh run-app.sh

local_ip=$(ip addr|grep -E "bond0|eth0"| awk '/^[0-9]+: / {}; /inet.*global/ {print gensub(/(.*)\/(.*)/, "\\1", "g", $2)}'|head -1)
local_ip=${local_ip:-Local_IP}

echo -e "
web access http://${local_ip}:1500/
user: admin
pass: admin123

"