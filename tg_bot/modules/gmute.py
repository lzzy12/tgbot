from telegram import Message, Update, Bot, User, Chat, ParseMode
from telegram.error import BadRequest, TelegramError
from telegram.ext import run_async, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import mention_html
from typing import Optional, List
import tg_bot.modules.sql.gmute_sql as sql
from tg_bot import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, STRICT_GBAN
from tg_bot.modules.helper_funcs.chat_status import user_admin, is_user_admin
from tg_bot.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from tg_bot.modules.helper_funcs.filters import CustomFilters
from tg_bot.modules.helper_funcs.misc import send_to_list
from tg_bot.modules.sql.users_sql import get_all_chats

GMUTE_ERRORS = {
    "User is an administrator of the chat",
    "Chat not found",
    "Not enough rights to restrict/unrestrict chat member",
    "User_not_participant",
    "Peer_id_invalid",
    "Group chat was deactivated",
    "Chat_admin_required",
    "Method is available only for supergroups",
    "Channel_private",
    "Not in the chat"
}

def gmute(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message
    muter = update.effective_user
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("You don't seem to be referring to a user.")
        return
    if int(user_id) in SUDO_USERS:
        message.reply_text("Cannot gmute sudo user!")
        return
    if int(user_id) in SUPPORT_USERS:
        message.reply_text("OOOH someone's trying to gmute a support user! *grabs popcorn*")
        return
    if user_id == bot.id:
        message.reply_text("NoU")
        return

    try:
        user_chat = bot.get_chat(user_id)
    except BadRequest as excp:
        message.reply_text(excp.message)
        return

    if user_chat.type != 'private':
        message.reply_text("That's not a user!")
        return
    if sql.is_user_gmuted(user_id):
        if not reason:
            message.reply_text("This user is already gmuted; I'd change the reason, but you haven't given me one...")
            return
        old_reason = sql.update_gmute_reason(user_id, user_chat.username or user_chat.first_name, reason)
        if old_reason:
            message.reply_text("This user is already gmuted, for the following reason:\n"
                               "<code>{}</code>\n"
                               "I've gone and updated it with your new reason!".format(html.escape(old_reason)),
                               parse_mode=ParseMode.HTML)
        else:
            message.reply_text("This user is already gmuted, but had no reason set; I've gone and updated it!")

        return

    message.reply_text("*KEK* User being gmuted!")
    send_to_list(bot, SUDO_USERS + SUPPORT_USERS,
                 "{} is gmuting user {} "
                 "because:\n{}".format(mention_html(muter.id, muter.first_name),
                                       mention_html(user_chat.id, user_chat.first_name), reason or "No reason given"),
                 html=True)
    sql.gmute_user(user_id, user_chat.username or user_chat.first_name, reason)
    chats = get_all_chats()
    for chat in chats:
        chat_id = chat.chat_id
        if not sql.does_chat_gmute(chat_id):
            continue
        try:
            bot.restrict_chat_member(chat.chat_id, user_id, can_send_messages=False)
        except BadRequest as excp:
            if excp.message in GMUTE_ERRORS:
                pass
            else:
                message.reply_text("Could not gmute due to: {}".format(excp.message))
                send_to_list(bot, SUDO_USERS + SUPPORT_USERS, "Could not gmute due to: {}".format(excp.message))
                sql.ungmute_user(user_id)
                return
        except TelegramError:
            pass
        send_to_list(bot, SUDO_USERS + SUPPORT_USERS, "Gmuted {}.".format(mention_html(user_chat.id, user_chat.first_name)))

GMUTE_HANDLER = CommandHandler("gmute", gmute, pass_args=True,
                              filters=CustomFilters.sudo_filter | CustomFilters.support_filter)
dispatcher.add_handler(GMUTE_HANDLER)
