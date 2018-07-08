import pyqrcode
from typing import List
from tg_bot import dispatcher
from telegram import Message, Chat, Update, Bot, ParseMode
from telegram.ext import CommandHandler, MessageHandler, Filters, run_async

def gen_qrcode(args: List[str]):
    char = str()
    for i in args:
        char += i + " "
    pyqrcode.create(char).png("new.png", scale=4)

@run_async
def send_qrcode(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message
    chat = update.effective_chat
    message.reply_text("Processing!")
    gen_qrcode(args)
    bot.send_photo(chat.id, open("new.png", 'rb'), caption="Done!")

QR_HANDLER = CommandHandler("qr", send_qrcode, pass_args=True)
dispatcher.add_handler(QR_HANDLER)

