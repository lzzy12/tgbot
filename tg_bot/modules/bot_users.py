import html, json, ast
from telegram import Message, Update, Bot, User, Chat, ParseMode
from telegram.error import BadRequest, TelegramError
from telegram.ext import run_async, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import mention_html
from tg_bot import dispatcher, OWNER_ID, SUDO_USERS
import tg_bot.modules.sql.users_sql as sql

@run_async
def listsudo(bot: Bot, update: Update):
    chat = update.effective_chat
    message = update.effective_message
    reply_msg = ""
    for i in SUDO_USERS:
       reply_msg += "\n" + str(i)

    message.reply_text("<b>SUDO USERS:</b> {}\n".format(html.escape(reply_msg)), parse_mode=ParseMode.HTML)
    return

__mod_name__ = "Bot users"
BOTUSER_HANDLER = CommandHandler("listsudo", listsudo)
dispatcher.add_handler(BOTUSER_HANDLER)
