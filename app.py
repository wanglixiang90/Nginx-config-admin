#!/usr/bin/env python
import os
import random
import string
import subprocess
import time
from os import listdir
from os.path import isfile, join
from flask import Flask, jsonify, render_template, request, redirect, url_for, g
from flask_httpauth import HTTPBasicAuth
from jinja2 import FileSystemLoader, Environment
import logging
from logging.handlers import RotatingFileHandler
from config import config

app = Flask(__name__)
auth = HTTPBasicAuth()
app.config.from_pyfile('config/config.py')

# 生成指定长度 num 的随机字符串, 26大写字母+纳秒戳
def random_name(num: int):
    rand_str = ''.join(random.sample(string.ascii_uppercase + str(time.time_ns()), num))
    return rand_str


def str_br(output=None):
    return output.replace('\n', '<br/>')


def tmessage(msg=None):
    if "successful" in msg or "\u786e\u5b9a" in msg:
        return jsonify({"title": "成功！", "msg": str_br(msg), "type": "success"})
    elif "failed" in msg or "\u5931\u8d25" in msg:
        return jsonify({"title": "失败！", "msg": str_br(msg), "type": "error"})
    return jsonify({"title": "信息！", "msg": str_br(msg), "type": "notice"})


@auth.get_password
def get_pw(username):
    users = dict(config.users.items('users'))
    if username in users:
        g.username = username
        return users.get(username)
    return None


def setup_log():
    """配置日志"""
    logsdir = "logs"
    if not os.path.exists(logsdir):
        os.makedirs(logsdir)

    # 设置日志的记录等级
    logging.basicConfig(level=logging.INFO)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/pynginx.log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    fmt = '[%(asctime)s] [%(levelname)s] [%(filename)s %(funcName)s %(lineno)s] %(message)s'
    formatter = logging.Formatter(fmt)
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)

    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


@app.route('/')
@auth.login_required
def index():
    return render_template('server.html')

@app.route('/nginx-server')
@auth.login_required
def nginx_server():
    files = [f for f in listdir(config.SERVER_PATH) if isfile(join(config.SERVER_PATH, f))]
    sites = []
    enable_conf = [f for f in listdir(config.EN_SRV_PATH) if isfile(join(config.EN_SRV_PATH, f))]

    for file in files:
        if file in enable_conf:
            sites.append({'file': file, 'choose': 'on'})
        else:
            sites.append({'file': file, 'choose': 'off'})
    return jsonify({'sites': sites})


@app.route('/nginx-status')
@auth.login_required
def nginx_status():
    status = ''
    output = subprocess.getoutput('service nginx status')
    if "active (running)" in output:
        status = 'running'
    if "inactive (dead)" in output or 'failed' in output:
        status = 'stop'
    return jsonify({'status': status})


@app.route('/user-config')
@auth.login_required
def user_config():
    with open(config.USER_FILE) as f:
        file = f.read()
    sub_title = "Edit user file"
    fm_url = "/save-user-config"
    app.logger.info('{} visit user-config'.format(g.username))
    return render_template('cmeditor.html', file=file, sub_title=sub_title , fm_url=fm_url)


@app.route('/save-user-config', methods=['POST'])
@auth.login_required
def save_user_config():
    with open(config.USER_FILE, "w") as f:
        f.write(request.form['file'])
    config.users.read(config.USER_FILE)
    app.logger.info('{} edit user_file'.format(g.username))
    return redirect(url_for('index'))


@app.route('/nginx-config')
@auth.login_required
def nginx_config():
    with open(config.CONFIG_FILE) as f:
        file = f.read()
    sub_title = "Edit Nginx.conf"
    fm_url = "/save-nginx-config"
    return render_template('cmeditor.html', file=file, sub_title=sub_title , fm_url=fm_url)


@app.route('/save-nginx-config', methods=['POST'])
@auth.login_required
def save_nginx_config():
    with open(config.CONFIG_FILE, "w") as f:
        f.write(request.form['file'])
    app.logger.info('{} edit nginx_config'.format(g.username))
    return redirect(url_for('index'))


# args_dict pathdir, name, fsuff, tmpl, server_port, **
@app.route('/save-site', methods=['POST'])
@auth.login_required
def save_site():
    fsuff = ''
    tmpl = ''
    argsdict = request.values.to_dict()
    name = argsdict.get('name')
    server_port = argsdict.get('serverport')
    servertype = argsdict.get('servertype')

    # name 为空，赋值随机字符
    if name == "":
        name = 'ngx_{}'.format(random_name(8))
    if server_port == "":
        server_port = "80"

    if servertype != "fileserver":
        upstream = argsdict.get('upstream')
        if upstream == "":
            upstream = "127.0.0.1:8080"
        ups_name = name + "_" + random_name(4)
        ups_list = upstream.strip().split("\r\n")
        # tmpl 动态赋值
        if servertype == "tcpproxy":
            tmpl = config.TCPPROXY
            fsuff = "stream"
        elif servertype == "udpproxy":
            tmpl = config.UDPPROXY
            fsuff = "stream"
        elif servertype == "httpproxy":
            tmpl = config.HTTPPROXY
            fsuff = "conf"
        content = {
            'server_name': name,
            'ups_name': ups_name,
            'server_port': server_port,
            'ups': ups_list
        }
    else:
        filepath = argsdict.get('filepath')
        tmpl = config.FILESERVER
        fsuff = "conf"
        if filepath.strip() == '':
            filepath = "/var/www/html"
        content = {
            'server_name': name,
            'server_port': server_port,
            'filepath': filepath
        }
    # 渲染模板配置文件，格式化输出文件
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(tmpl)  # 获取模板文件
    conftext = template.render(content)
    # 写入配置文件
    fname = '{}.{}'.format(name, fsuff)
    with open('{}/{}'.format(config.SERVER_PATH, fname), "w") as f:
        f.write(conftext)
    app.logger.info('{} create config {}'.format(g.username, fname))
    sub_title = "Edit server {}".format(fname)
    fm_url = "/update-site?name={}".format(fname)
    return render_template('cmeditor.html', file=conftext, sub_title=sub_title, fm_url=fm_url)


@app.route('/rename-site', methods=['POST'])
@auth.login_required
def rename_site():
    argsdict = request.values.to_dict()
    src_name = argsdict.get('src_name', '')
    new_name = argsdict.get('new_name', '')
    src_file_en = '{}/{}'.format(config.EN_SRV_PATH, src_name)
    src_file = '{}/{}'.format(config.SERVER_PATH, src_name)
    new_file_en = '{}/{}'.format(config.EN_SRV_PATH, new_name)
    new_file = '{}/{}'.format(config.SERVER_PATH, new_name)
    subprocess.call("mv {} {}".format(src_file_en, new_file_en), shell=True)
    subprocess.call("mv {} {}".format(src_file, new_file), shell=True)
    return jsonify({"title": "成功！", "msg": "server名称修改完成.", "type": "success"})


@app.route('/edit-site', methods=['POST'])
@auth.login_required
def edit_site():
    argsdict = request.values.to_dict()
    name = argsdict.get('name', '')
    with open('{}/{}'.format(config.SERVER_PATH, name)) as f:
        file = f.read()
    sub_title = "Edit server {}".format(name)
    fm_url = "/update-site?name={}".format(name)
    return render_template('cmeditor.html', file=file, sub_title=sub_title, fm_url=fm_url)


@app.route('/update-site', methods=['POST'])
@auth.login_required
def update_site():
    name = request.args.get('name', '')
    # windows / linux 文件换行问题
    with open('{}/{}'.format(config.SERVER_PATH, name), "w", newline='\n') as f:
        f.write(request.form['file'])
    app.logger.info('{} update config {}'.format(g.username, name))
    return redirect(url_for('index'))


@app.route('/delete-site')
@auth.login_required
def delete_site():
    name = request.args.get('name', '')
    enfile = '{}/{}'.format(config.EN_SRV_PATH, name)
    subprocess.call("rm -f " + enfile, shell=True)
    file = '{}/{}'.format(config.SERVER_PATH, name)
    subprocess.call("rm -f " + file, shell=True)
    app.logger.info('{} delete config {}'.format(g.username, name))
    return jsonify({"title": "成功！", "msg": "删除完成.", "type": "success"})


@app.route('/enable-site')
@auth.login_required
def enable_site():
    name = request.args.get('name', '')
    file = '{}/{}'.format(config.SERVER_PATH, name)
    link = '{}/{}'.format(config.EN_SRV_PATH, name)
    subprocess.call("ln {} {}".format(file, link), shell=True)
    app.logger.info('{} enable config {}'.format(g.username, name))
    return jsonify({"title": "成功！", "msg": "开启完成.", "type": "success"})


@app.route('/disable-site')
@auth.login_required
def disable_site():
    name = request.args.get('name', '')
    file = '{}/{}'.format(config.EN_SRV_PATH, name)
    subprocess.call("rm -f " + file, shell=True)
    app.logger.info('{} disable config {}'.format(g.username, name))
    return jsonify({"title": "关闭！", "msg": "完成关闭.", "type": "success"})


@app.route('/start-nginx')
@auth.login_required
def start_nginx():
    output = subprocess.getoutput('service nginx start')
    if "failed" in output or "\u5931\u8d25" in output:
        tmp_str = subprocess.getoutput('service nginx status |grep "Address already in use"|grep -v grep')
        msg = tmp_str.split("\n")[0]
        app.logger.info('{} start nginx failed'.format(g.username))
        return jsonify({"title": "失败！", "msg": msg, "type": "error"})
    app.logger.info('{} start nginx'.format(g.username))
    return tmessage(output)


@app.route('/stop-nginx')
@auth.login_required
def stop_nginx():
    output = subprocess.getoutput('service nginx stop')
    app.logger.info('{} stop nginx'.format(g.username))
    return tmessage(output)


@app.route('/reload-nginx')
@auth.login_required
def reload_nginx():
    output = subprocess.getoutput('service nginx reload')
    if "failed" in output or "invalid" in output or "\u5931\u8d25" in output:
        tmp_str = subprocess.getoutput('service nginx status')
        if 'inactive (dead)' in tmp_str:
            app.logger.info('{} reload nginx failed'.format(g.username))
            return jsonify({"title": "失败！", "msg": "Nginx service is not running", "type": "error"})
    app.logger.info('{} reload nginx'.format(g.username))
    return tmessage(output)


@app.route('/test-nginx')
@auth.login_required
def test_nginx():
    output = subprocess.getoutput('service nginx configtest')
    return tmessage(output)


if __name__ == '__main__':
    setup_log()
    app.run(debug=True, host='0.0.0.0', port=1500)
