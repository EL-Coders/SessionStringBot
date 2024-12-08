import traceback
from data import Data
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, LinkPreviewOptions
from ssnbot.plugins.generate import generate_session, ask_ques, buttons_ques
from ssnbot import LOGGER


@Client.on_callback_query(filters.regex(r"^home$"))
async def home(bot, query):
    user = bot.me
    mention = user.mention
    chat_id = query.from_user.id
    message_id = query.message.id
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=Data.START.format(query.from_user.mention, mention),
        reply_markup=InlineKeyboardMarkup(Data.buttons),
    )


@Client.on_callback_query(filters.regex(r"^about$"))
async def about(bot, query):
    chat_id = query.from_user.id
    message_id = query.message.id
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=Data.ABOUT,
        # disable_web_page_preview=True,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        reply_markup=InlineKeyboardMarkup(Data.home_buttons),
    )


@Client.on_callback_query(filters.regex(r"^help$"))
async def help(bot, query):
    chat_id = query.from_user.id
    message_id = query.message.id
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=Data.HELP,
        # disable_web_page_preview=True,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        reply_markup=InlineKeyboardMarkup(Data.home_buttons),
    )


@Client.on_callback_query(filters.regex(r"^generate$"))
async def generate(bot, query):
    await query.answer("Select your library")
    await query.message.reply(ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques))


@Client.on_callback_query(filters.regex(r"^pyrogram$"))
async def pyro(bot, query):
    try:
        await query.answer(
            "Please note that the new type of string sessions may not work in all bots, i.e, only the bots that have been updated to pyrogram v2 will work!",
            show_alert=True,
        )
        await generate_session(bot, query.message)
    except Exception as e:
        LOGGER.error(traceback.format_exc())
        LOGGER.error(e)
        await query.message.reply(ERROR_MESSAGE.format(str(e)))


@Client.on_callback_query(filters.regex(r"^telethon$"))
async def tele(bot, query):
    try:
        await query.answer()
        await generate_session(bot, query.message, telethon=True)
    except Exception as e:
        LOGGER.error(traceback.format_exc())
        LOGGER.error(e)
        await query.message.reply(ERROR_MESSAGE.format(str(e)))


ERROR_MESSAGE = (
    "Oops! An exception occurred! \n\n**Error** : {} "
    "\n\nPlease visit @ElUpdates if this message doesn't contain any "
    "sensitive information and you if want to report this as "
    "this error message is not being logged by us!"
)
