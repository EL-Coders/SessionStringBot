import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from env import AUTH_USERS
from StringSessionBot.db.sql import query_msg
from StringSessionBot.db.support import users_info


@Client.on_message(filters.private & filters.command("stats"))
async def get_subscribers_count(bot: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in AUTH_USERS:
        return
    wait_msg = "__Calculating, please wait...__"
    msg = await message.reply_text(wait_msg)
    active, blocked = await users_info(bot)
    stats_msg = f"**Stats**\nSubscribers: `{active}`\nBlocked / Deleted: `{blocked}`"
    await msg.edit(stats_msg)


@Client.on_message(filters.private & filters.command("broadcast"))
async def send_text(bot, message: Message):
    user_id = message.from_user.id
    if user_id not in AUTH_USERS:
        return

    if "broadcast" in message.text and message.reply_to_message is not None:
        query = await query_msg()
        for row in query:
            chat_id = int(row[0])
            try:
                await bot.copy_message(
                    chat_id=chat_id,
                    from_chat_id=message.chat.id,
                    message_id=message.reply_to_message_id,
                    caption=message.reply_to_message.caption,
                    reply_markup=message.reply_to_message.reply_markup,
                )
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                pass
    else:
        reply_error = (
            "`Use this command as a reply to any telegram message without any spaces.`"
        )
        msg = await message.reply_text(reply_error, message.id)
        await asyncio.sleep(8)
        await msg.delete()
