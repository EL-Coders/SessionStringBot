#  !/usr/bin/env python3
#  -*- coding: utf-8 -*-
#  Name     : broadcast-bot [ Telegram ]
#  Repo     : https://github.com/m4mallu/broadcast-bot
#  Author   : Renjith Mangal [ https://t.me/space4renjith ]
#  Licence  : GPL-3

import os
import asyncio
from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from StringSessionBot.db.support import users_info
from StringSessionBot.db.sql import add_user, query_msg
from env import AUTH_USERS


# if bool(os.environ.get("ENV", False)):
#     from sample_config import Config
# else:
#     from config import Config


# # ------------------------------- Start Message --------------------------------- #
# @Client.on_message(filters.private & filters.command('start'))
# async def start_bot(bot, m: Message):
#     id = m.from_user.id
#     user_name = '@' + m.from_user.username if m.from_user.username else None
#     await add_user(id, user_name)
#     await m.reply_text(Presets.WELCOME_MESSAGE.format(m.from_user.mention(),
#                                                       Config.SUPPORT_CHAT if Config.SUPPORT_CHAT else "_______"),
#                        parse_mode='html',
#                        disable_web_page_preview=True
#                        )


# ------------------------------- View Subscribers --------------------------------- #
@Client.on_message(filters.private & filters.command('subscribers'))
async def subscribers_count(bot, m: Message):
    id = m.from_user.id
    if id not in AUTH_USERS:
        return
    WAIT_MSG = "<b>Please Wait...</b>"
    msg = await m.reply_text(WAIT_MSG)
    messages = await users_info(bot)
    active = messages[0]
    blocked = messages[1]
    await m.delete()
    USERS_LIST = "<b>Total:</b>\n\nSubscribers - {}\nBlocked / Deleted - {}"
    await msg.edit(USERS_LIST.format(active, blocked))


# ------------------------ Send messages to subs ----------------------------- #
@Client.on_message(filters.private & filters.command('send'))
async def send_text(bot, m: Message):
    id = m.from_user.id
    if id not in AUTH_USERS:
        return
    if (" " not in m.text) and ("send" in m.text) and (m.reply_to_message is not None):       
        query = await query_msg()
        for row in query:
            chat_id = int(row[0])
            try:
                await bot.copy_message(
                    chat_id=chat_id,
                    from_chat_id=m.chat.id,
                    message_id=m.reply_to_message_id,
                    caption=m.reply_to_message.caption,
                    reply_markup=m.reply_to_message.reply_markup
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except Exception:
                pass
    else:
        REPLY_ERROR = "<code>Use this command as a reply to any telegram message with out any spaces.</code>"
        msg = await m.reply_text(REPLY_ERROR, m.id)
        await asyncio.sleep(8)
        await msg.delete()