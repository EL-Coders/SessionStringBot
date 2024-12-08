import asyncio
from pyrogram import Client, filters
from pyrogram.errors import (
    ApiIdInvalid,
    PasswordHashInvalid,
    PhoneCodeExpired,
    PhoneCodeInvalid,
    PhoneNumberInvalid,
    SessionPasswordNeeded,
    PhoneNumberBanned,
    PhonePasswordFlood,
    AccessTokenInvalid,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from telethon import TelegramClient
from telethon.errors import (
    ApiIdInvalidError,
    PasswordHashInvalidError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
    AccessTokenInvalidError,
)
from telethon.sessions import StringSession

from data import Data
from ssnbot import LOGGER

ask_ques = "Please choose the python library you want to generate string session for"
buttons_ques = [
    [
        InlineKeyboardButton("Pyrogram", callback_data="pyrogram"),
        InlineKeyboardButton("Telethon", callback_data="telethon"),
    ],
]


@Client.on_message(filters.private & ~filters.forwarded & filters.command("generate"))
async def main(_, msg):
    await msg.reply(ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques))


async def generate_session(
    bot: Client,
    msg: Message,
    telethon=False,
    old_pyro: bool = False,
    is_bot: bool = False,
):
    if telethon:
        ty = "Telethon"
    else:
        ty = "Pyrogram"
    if is_bot:
        ty += " Bot"
    await msg.reply(f"Starting {ty} Session Generation...")

    user_id = msg.chat.id
    try:
        api_id_msg = await bot.ask_message(
            user_id, "Please send your `API_ID`", filters=filters.text, timeout=360
        )
    except TimeoutError:
        await msg.reply_text("Request timed out, please try again with /start")
        return

    if await cancelled(api_id_msg):
        await bot.cancel_message_listener(chat_id=user_id)
        return

    try:
        api_id = int(api_id_msg.text)
    except ValueError:
        await api_id_msg.reply(
            "Not a valid API_ID (which must be an integer). Please start generating session again.",
            quote=True,
            reply_markup=InlineKeyboardMarkup(Data.generate_button),
        )
        return

    try:
        api_hash_msg = await bot.ask_message(
            user_id, "Please send your `API_HASH`", filters=filters.text, timeout=360
        )
    except TimeoutError:
        await msg.reply_text("Request timed out, please try again with /start")
        return
    if await cancelled(api_hash_msg):
        await bot.cancel_message_listener(chat_id=user_id)
        return

    api_hash = api_hash_msg.text
    if not is_bot:
        t = "Now please send your `PHONE_NUMBER` along with the country code. \nExample : `+19876543210`'"
    else:
        t = "Now please send your `BOT_TOKEN` \nExample : `12345:abcdefghijklmnopqrstuvwxyz`'"

    try:
        phone_number_msg = await bot.ask_message(
            user_id, t, filters=filters.text, timeout=360
        )
    except TimeoutError:
        await msg.reply_text("Request timed out, please try again with /start")
        return
    if await cancelled(phone_number_msg):
        await bot.cancel_message_listener(chat_id=user_id)
        return

    phone_number = phone_number_msg.text
    await msg.reply("Sending OTP...")

    if telethon and is_bot:
        clientt = TelegramClient(StringSession(), api_id, api_hash)
        await clientt.start(bot_token=phone_number)
    elif telethon:
        clientt = TelegramClient(StringSession(), api_id, api_hash)
    elif is_bot:
        clientt = Client(
            name="bot",
            api_id=api_id,
            api_hash=api_hash,
            bot_token=phone_number,
            in_memory=True,
        )
    else:
        clientt = Client(
            name="sess_user", api_id=api_id, api_hash=api_hash, in_memory=True
        )

    try:
        await clientt.connect()
    except Exception as e:
        LOGGER.error(e)

    try:
        code = None
        if not is_bot:
            if telethon:
                code = await clientt.send_code_request(phone_number)
            else:
                code = await clientt.send_code(phone_number)
    except (ApiIdInvalid, ApiIdInvalidError):
        await msg.reply(
            "`API_ID` and `API_HASH` combination is invalid. Please start generating session again.",
            reply_markup=InlineKeyboardMarkup(Data.generate_button),
        )
        return
    except (PhoneNumberInvalid, PhoneNumberInvalidError):
        await msg.reply(
            "`PHONE_NUMBER` is invalid. Please start generating session again.",
            reply_markup=InlineKeyboardMarkup(Data.generate_button),
        )
        return
    except PhoneNumberBanned:
        await msg.reply("`PHONE_NUMBER` is banned, please try with another number.")
        return
    except PhonePasswordFlood:
        await msg.reply(
            "Unable to send code, you have tried logging in too many times."
        )
        return

    try:
        phone_code_msg = None
        if not is_bot:
            phone_code_msg = await bot.ask_message(
                user_id,
                "Please check for an OTP in official telegram account. If you got it, send OTP here after reading the below format. \nIf OTP is `12345`, **please send it as** `1 2 3 4 5`.",
                filters=filters.text,
                timeout=360,
            )
            if await cancelled(phone_code_msg):
                return
    except TimeoutError:
        await msg.reply(
            "Time limit reached of 5 minutes. Please start generating session again by tapping /start.",
            reply_markup=InlineKeyboardMarkup(Data.generate_button),
        )
        return

    if not is_bot:
        phone_code = phone_code_msg.text.replace(" ", "")
        try:
            if telethon:
                await clientt.sign_in(phone_number, phone_code, password=None)
            else:
                await clientt.sign_in(phone_number, code.phone_code_hash, phone_code)
        except (PhoneCodeInvalid, PhoneCodeInvalidError):
            await msg.reply(
                "OTP is invalid. Please start generating session again.",
                reply_markup=InlineKeyboardMarkup(Data.generate_button),
            )
            return
        except (PhoneCodeExpired, PhoneCodeExpiredError):
            await msg.reply(
                "OTP is expired. Please start generating session again.",
                reply_markup=InlineKeyboardMarkup(Data.generate_button),
            )
            return
        except (
            SessionPasswordNeeded,
            SessionPasswordNeededError,
        ):
            try:
                two_step_msg = await bot.ask_message(
                    user_id,
                    "Your account has enabled two-step verification. Please provide the password.",
                    filters=filters.text,
                    timeout=300,
                )
            except TimeoutError:
                await msg.reply(
                    "Time limit reached of 5 minutes. Please start generating session again by tapping /start.",
                    reply_markup=InlineKeyboardMarkup(Data.generate_button),
                )
                return
            try:
                password = two_step_msg.text
                if telethon:
                    await clientt.sign_in(password=password)
                else:
                    await clientt.check_password(password=password)
                if await cancelled(api_id_msg):
                    return
            except (
                PasswordHashInvalid,
                PasswordHashInvalidError,
            ):
                await two_step_msg.reply(
                    "Invalid Password Provided. Please start generating session again.",
                    quote=True,
                    reply_markup=InlineKeyboardMarkup(Data.generate_button),
                )
                return
    else:
        try:
            if telethon:
                await clientt.start(bot_token=phone_number)
            else:
                await clientt.sign_in_bot(phone_number)
        except (AccessTokenInvalid, AccessTokenInvalidError):
            await msg.reply(
                "`BOT_TOKEN` is invalid. Please start generating session again.",
                reply_markup=InlineKeyboardMarkup(Data.generate_button),
            )
            return

    try:
        if telethon:
            string_session = clientt.session.save()
        else:
            string_session = await clientt.export_session_string()
    except Exception as e:
        LOGGER.error(e)

    text = f"**{ty.upper()} STRING SESSION** \n\n`{string_session}` \n\nGenerated by @SessionStringzBot"
    try:
        if not is_bot:
            await clientt.send_message("me", text)
        else:
            await bot.send_message(msg.chat.id, text)
    except KeyError as e:
        LOGGER.error(e)

    try:
        await clientt.disconnect()
    except Exception as e:
        LOGGER.error(e)

    await bot.send_message(
        msg.chat.id,
        "Successfully generated {} string session. \n\nPlease check your saved messages! \n\nBy @ELUpdates".format(
            "telethon" if telethon else "pyrogram"
        ),
    )


async def cancelled(msg):
    if "/cancel" in msg.text:
        await msg.reply(
            "Cancelled the Process!",
            quote=True,
            reply_markup=InlineKeyboardMarkup(Data.generate_button),
        )
        return True
    elif "/restart" in msg.text:
        await msg.reply(
            "Restarted the Bot!",
            quote=True,
            reply_markup=InlineKeyboardMarkup(Data.generate_button),
        )
        return True
    elif msg.text.startswith("/"):  # Bot Commands
        await msg.reply("Cancelled the generation process!", quote=True)
        return True
    else:
        return False
