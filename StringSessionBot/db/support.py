#  !/usr/bin/env python3
#  -*- coding: utf-8 -*-
#  Name     : broadcast-bot [ Telegram ]
#  Repo     : https://github.com/m4mallu/broadcast-bot
#  Author   : Renjith Mangal [ https://t.me/space4renjith ]
#  Licence  : GPL-3

import asyncio
from StringSessionBot.db.sql import query_msg
from pyrogram.errors import FloodWait
from pyrogram import enums

async def users_info(bot):
    users = 0
    blocked = 0
    identity = await query_msg()
    for id in identity:
        name = bool()
        try:
            name = await bot.send_chat_action(int(id[0]), enums.ChatAction.TYPING)
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except Exception:
            pass
        if bool(name):
            users += 1
        else:
            blocked += 1
    return users, blocked