#!/usr/bin/env python
import configparser

SECRET_KEY = 'e786b7872cba30733fdad66f70abf6fa'
# http auth 简单用户认证配置文件
USER_FILE = 'config/users.ini'
users = configparser.ConfigParser()
users.read(USER_FILE)

# config files path
CONFIG_PATH = '/etc/nginx'
CONFIG_FILE = CONFIG_PATH + '/nginx.conf'
SERVER_PATH = CONFIG_PATH + '/sites-available'
EN_SRV_PATH = CONFIG_PATH + '/sites-enabled'

# nginx server templates
TCPPROXY = 'tcpproxy.j2'
UDPPROXY = 'udpproxy.j2'
HTTPPROXY = 'httpproxy.j2'
FILESERVER = 'fileserver.j2'
