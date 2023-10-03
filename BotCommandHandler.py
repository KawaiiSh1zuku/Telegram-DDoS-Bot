from telegram import Update, constants
from telegram.ext import ContextTypes
import Database
from Config import config
import time

database_file = config.DATABASE.database_file
botdb = Database.BotDatabase(database_file)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="欢迎使用 Ayachi Network Stresser\n发送 /help 查看帮助\n新用户发送 /register 注册")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="*Ayachi Network Stresser*\n/attack \\- 提交任务\n/methods \\- 方法列表\n/info \\- 用户信息\n/checkin \\- 签到\n\n*Coded with ❤ by @KawaiiSh1zuku*", parse_mode=constants.ParseMode.MARKDOWN_V2)

async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="*Ayachi Network Stresser 管理员命令*\n/ban \\- 封禁用户\n/set\\_credit \\- 设置用户积分\n/set\\_cooldown \\- 设置用户冷却时长\n\n*Coded with ❤ by @KawaiiSh1zuku*", parse_mode=constants.ParseMode.MARKDOWN_V2)

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if(botdb.register(user_id, int(time.time()))):
        response_text = "注册成功！"
    else:
        response_text = "注册失败，用户已注册或被封禁。"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    response_text = botdb.checkin(user_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text, parse_mode=constants.ParseMode.MARKDOWN_V2)

async def user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_firstname = update.effective_user.first_name
    credit, formatted_time = botdb.search_user_info(user_id)
    if(credit != -1):
        response_text = f'''👤用户: {user_firstname}\n🆔用户ID: `{user_id}`\n⭐️剩余积分: {credit}\n🍃上次签到: {formatted_time}'''
    else:
        response_text = "未注册或被封禁用户"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text, parse_mode=constants.ParseMode.MARKDOWN_V2)

async def admin_ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    if len(context.args) != 1:
        response_text = "命令用法: /ban user_id"
    else:
        user_id = context.args[0]
        if(botdb.admin_ban_user(telegram_id, user_id)):
            response_text = "封禁成功"
        else:
            response_text = "用户未注册或你无权操作"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

async def admin_set_credit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    if len(context.args) != 2:
        response_text = "命令用法: /set_credit user_id credit"
    else:
        user_id = context.args[0]
        credit = context.args[1]
        if(botdb.admin_set_credit(telegram_id, user_id, credit)):
            response_text = "设置成功"
        else:
            response_text = "用户未注册或你无权操作"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

async def admin_set_cooldown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    if len(context.args) != 2:
        response_text = "命令用法: /set_cooldown user_id cooldown (second)"
    else:
        user_id = context.args[0]
        cooldown = context.args[1]
        if(botdb.admin_set_cooldown(telegram_id, user_id, cooldown)):
            response_text = "设置成功"
        else:
            response_text = "用户未注册或你无权操作"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

async def methods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response_text = botdb.get_methods()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text, parse_mode=constants.ParseMode.MARKDOWN_V2)

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    if len(context.args) != 4:
        response_text = "命令用法: /attack 目标 端口 时间 模式"
    else:
        target = context.args[0].strip().split('&')[0].split('|')[0].split(';')[0].split('$')[0].split('>')[0].split('<')[0] # 屏蔽可能出现注入的字符
        port = context.args[1]
        duration = context.args[2]
        method = context.args[3]
        sql_ban = "~!@#$%^&*()+*/<>,.[]\/"
        response_text = ""
        isGoodSQL = False
        for i in sql_ban:
            if i in method:
                isGoodSQL = False
                break
            else:
                isGoodSQL = True
        if isGoodSQL:
            response_text = botdb.attack(telegram_id, target, port, duration, method)
        else:
            response_text = "不合法的模式"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text, parse_mode=constants.ParseMode.MARKDOWN_V2)