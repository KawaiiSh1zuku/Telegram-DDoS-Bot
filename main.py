import logging
from telegram import Update, Bot, BotCommand
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from Config import config
import BotCommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

bot_token = config.TELEGRAM.bot_token
admin_id = config.TELEGRAM.admin_id
database_file = config.DATABASE.database_file
IfProxy = config.PROXY.proxy
cur = None

if(IfProxy):
    proxy_url = config.PROXY.proxy_url
else:
    proxy_url = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="欢迎使用 Ayachi Network Stresser\n发送 /help 查看帮助")

async def setCommands():
    # 这里一直报错 改不好
    commands = [
        BotCommand("help", "获取机器人帮助"),
        BotCommand("my", "获取用户信息"),
        BotCommand("methods", "获取攻击方法列表"),
        BotCommand("attack", "进行攻击"),
    ]
    try:
        await Bot.set_my_commands(commands)
    except:
        pass

if __name__ == '__main__':
    application = ApplicationBuilder().token(bot_token).get_updates_proxy_url(proxy_url).build()

    # 管理员命令
    ban_handler = CommandHandler('ban', BotCommandHandler.admin_ban_user)
    application.add_handler(ban_handler)
    set_credit_handler = CommandHandler('set_credit', BotCommandHandler.admin_set_credit)
    application.add_handler(set_credit_handler)

    # 用户命令
    start_handler = CommandHandler('start', BotCommandHandler.start)
    application.add_handler(start_handler)
    register_handler = CommandHandler('register', BotCommandHandler.register)
    application.add_handler(register_handler)
    checkin_handler = CommandHandler('checkin', BotCommandHandler.checkin)
    application.add_handler(checkin_handler)
    info_handler = CommandHandler('my', BotCommandHandler.user_info)
    application.add_handler(info_handler)
    method_handler = CommandHandler('methods', BotCommandHandler.methods)
    application.add_handler(method_handler)
    attack_handler = CommandHandler('attack', BotCommandHandler.attack)
    application.add_handler(attack_handler)
    attack_handler = CommandHandler('help', BotCommandHandler.help)
    application.add_handler(attack_handler)

    application.run_polling()