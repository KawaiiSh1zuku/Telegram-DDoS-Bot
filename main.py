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

if IfProxy:
    proxy_url = config.PROXY.proxy_url
else:
    proxy_url = None

async def set_commands(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.set_my_commands(commands=[
        ("help", "命令指南"),
        ("checkin", "每日签到"),
        ("info", "个人信息"),
        ("methods", "方法列表"),
        ("attack", "进行攻击"),
    ])

if __name__ == '__main__':
    application = ApplicationBuilder().token(bot_token).get_updates_proxy_url(proxy_url).build()
    job_queue = application.job_queue
    job_queue.run_once(set_commands, 1)

    # 管理员命令
    ban_handler = CommandHandler('ban', BotCommandHandler.admin_ban_user)
    application.add_handler(ban_handler)
    set_credit_handler = CommandHandler('set_credit', BotCommandHandler.admin_set_credit)
    application.add_handler(set_credit_handler)
    set_cooldown_handler = CommandHandler('set_cooldown', BotCommandHandler.admin_set_cooldown)
    application.add_handler(set_cooldown_handler)
    admin_handler = CommandHandler('admin', BotCommandHandler.admin_help)
    application.add_handler(admin_handler)

    # 用户命令
    start_handler = CommandHandler('start', BotCommandHandler.start)
    application.add_handler(start_handler)
    register_handler = CommandHandler('register', BotCommandHandler.register)
    application.add_handler(register_handler)
    checkin_handler = CommandHandler('checkin', BotCommandHandler.checkin)
    application.add_handler(checkin_handler)
    info_handler = CommandHandler('info', BotCommandHandler.user_info)
    application.add_handler(info_handler)
    method_handler = CommandHandler('methods', BotCommandHandler.methods)
    application.add_handler(method_handler)
    attack_handler = CommandHandler('attack', BotCommandHandler.attack)
    application.add_handler(attack_handler)
    attack_handler = CommandHandler('help', BotCommandHandler.help)
    application.add_handler(attack_handler)

    application.run_polling()