# Nginx-config-admin
nginx web config admin

## 1 install nginx in system
yum install -y nginx  (centos)<br>
apt install -y nginx  (debian)

## 2 git clone Nginx-config-admin
git clone https://github.com/wanglixiang90/Nginx-config-admin.git

## 3 check python version, use python3.7
python -V  or python3 -V

## 4 init app
"bash init.sh" or "sudo sh init.sh"

## 5 run app
python app.py

web http://you_IP:1500<br>
default user/pass  admin/admin123

## 6 use web admin and edit nginx.conf
add  "include /etc/nginx/sites-enabled/*.conf;" in http{ } config <br>
append in end <br>
"stream {
	include /etc/nginx/sites-enabled/*.stream;
}"

