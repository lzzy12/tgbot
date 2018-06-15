import html
from typing import Optional, List
from telegram import Message, Chat, Update, Bot, User
from telegram import ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown, mention_html
from tg_bot.modules.helper_funcs.filters import CustomFilters
from tg_bot.modules.helper_funcs.extraction import extract_user
from tg_bot import dispatcher, SUDO_USERS, OWNER_USERNAME, OWNER_ID

with open("sudo_users.txt", 'r') as file:
    for line in file:
        SUDO_USERS.append(line)


def add_to_sudo(user_id):
    with open("sudo_users.txt", 'a') as outfile:
        outfile.write(user_id)
    SUDO_USERS.append(user_id)   #So that bot need not to be restarted after each gpromotions


@run_async
def gpromote(bot: Bot, update: Update):
    args = List[str]
    message = update.effective_message
    banner = update.effective_user
    user_id = extract_user(message, args)
    if banner.id == OWNER_ID:
        if not user_id:
            message.reply_text("You don't seems to be referring to a user.")
            return
        elif int(user_id) in SUDO_USERS:
            message.reply_text("The user is already a sudo user.")
            return
        elif int(user_id) == OWNER_ID:
            message.reply_text("The specified user is my owner! No need add him to SUDO_USERS list!")
            return
        else:
            add_to_sudo(user_id)
            message.reply_text("Succefully added to SUDO user list!!")
            return
    else:
        message.reply_text("Only owner of the bot, {} can do this".format(OWNER_USERNAME))
        return

GPROMOTE_HANDLER = CommandHandler("gpromote", gpromote, filters = CustomFilters.sudo_filter)
dispatcher.add_handler(GPROMOTE_HANDLER)

