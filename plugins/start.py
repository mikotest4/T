import asyncio
import os
import random
import sys
import re
import string 
import string as rohit
import time
from datetime import datetime, timedelta
from pytz import timezone
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, 
    ReplyKeyboardMarkup, ChatInviteLink, ChatPrivileges
)
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant
from bot import Bot
from config import *
from helper_func import *
from database.database import *
from database.db_premium import *

BAN_SUPPORT = f"{BAN_SUPPORT}"
TUT_VID = f"{TUT_VID}"

#=====================================================================================##

@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    id = message.from_user.id
    is_premium = await is_premium_user(id)

    # Check if user is banned
    banned_users = await db.get_ban_users()
    if user_id in banned_users:
        return await message.reply_text(
            "<b>⛔️ You are Bᴀɴɴᴇᴅ from using this bot.</b>\n\n"
            "<i>Contact support if you think this is a mistake.</i>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Contact Support", url=BAN_SUPPORT)]]
            )
        )

    # ✅ Check Force Subscription FIRST (priority check)
    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    # Check if user is an admin and treat them as verified
    if user_id in await db.get_all_admins():
        verify_status = {
            'is_verified': True,
            'verify_token': None, 
            'verified_time': time.time(),
            'link': ""
        }
    else:
        verify_status = await db.get_verify_status(id)

        # NOW check token verification (only after force sub is satisfied)
        if SHORTLINK_URLS and SHORTLINK_APIS:
            # Fix: Ensure verified_time is a number before comparison
            verified_time = verify_status.get('verified_time', 0)
            try:
                verified_time = float(verified_time) if verified_time else 0
            except (ValueError, TypeError):
                verified_time = 0

            if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verified_time):
                await db.update_verify_status(user_id, is_verified=False)

            if "verify_" in message.text:
                _, token = message.text.split("_", 1)
                if verify_status['verify_token'] != token:
                    return await message.reply("Your token is invalid or expired. Try again by clicking /start.")
                await db.update_verify_status(id, is_verified=True, verified_time=time.time())
                
                current = await db.get_verify_count(id)
                await db.set_verify_count(id, current + 1)
                if verify_status["link"] == "":
                    reply_markup = None
                return await message.reply(
                    f"Your token has been successfully verified and is valid for {get_exp_time(VERIFY_EXPIRE)}",
                    reply_markup=reply_markup,
                    protect_content=False,
                    quote=True
                )

            if not verify_status['is_verified'] and not is_premium:
                token = ''.join(random.choices(rohit.ascii_letters + rohit.digits, k=10))
                await db.update_verify_status(id, verify_token=token, link="")
                
                # Use rotated shortener system
                original_link = f'https://telegram.dog/{client.username}?start=verify_{token}'
                link = await get_shortlink_rotated(user_id, original_link)
                
                # Get user's shortener status for display
                shortener_status = await get_user_shortener_status(user_id)
                
                btn = [
                    [InlineKeyboardButton("• ᴏᴘᴇɴ ʟɪɴᴋ •", url=link), 
                    InlineKeyboardButton('• ᴛᴜᴛᴏʀɪᴀʟ •', url=TUT_VID)],
                    [InlineKeyboardButton('• ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •', callback_data='premium')]
                ]
                
                # Enhanced message with rotation info
                cycle_info = ""
                if shortener_status['cycle_complete']:
                    cycle_info = "\n🔄 <i>Starting new verification cycle</i>"
                else:
                    current_shortener = shortener_status['shortener_names'][shortener_status['next_shortener']]
                    cycle_info = f"\n📊 <i>Step {shortener_status['used_count'] + 1}/{shortener_status['total_shorteners']} in current cycle ({current_shortener})</i>"
                
                return await message.reply(
                    f"𝗬𝗼𝘂𝗿 𝘁𝗼𝗸𝗲𝗻 𝗵𝗮𝘀 𝗲𝘅𝗽𝗶𝗿𝗲𝗱. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗿𝗲𝗳𝗿𝗲𝘀𝗵 𝘆𝗼𝘂𝗿 𝘁𝗼𝗸𝗲𝗻 𝘁𝗼 𝗰𝗼𝗻𝘁𝗶𝗻𝘂𝗲..\n\n"
                    f"<b>Tᴏᴋᴇɴ Tɪᴍᴇᴏᴜᴛ:</b> {get_exp_time(VERIFY_EXPIRE)}\n\n"
                    f"<b>ᴡʜᴀᴛ ɪs ᴛʜᴇ ᴛᴏᴋᴇɴ??</b>\n\n"
                    f"ᴛʜɪs ɪs ᴀɴ ᴀᴅs ᴛᴏᴋᴇɴ. ᴘᴀssɪɴɢ ᴏɴᴇ ᴀᴅ ᴀʟʟᴏᴡs ʏᴏᴜ ᴛᴏ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ ғᴏʀ {get_exp_time(VERIFY_EXPIRE)} ᴀғᴛᴇʀ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ."
                    f"{cycle_info}",
                    reply_markup=InlineKeyboardMarkup(btn),
                    protect_content=False,
                    quote=True
                )

    # File auto-delete time in seconds - Fix: Ensure it's an integer
    try:
        FILE_AUTO_DELETE = await db.get_del_timer()
        if not isinstance(FILE_AUTO_DELETE, int):
            FILE_AUTO_DELETE = int(FILE_AUTO_DELETE) if FILE_AUTO_DELETE else 600
    except (ValueError, TypeError):
        FILE_AUTO_DELETE = 600

    # Add the user if they're not in the database
    if not await db.present_user(user_id):
        try:
            await db.add_user(user_id)
        except Exception as e:
            print(f"Error adding user {user_id}: {e}")

    # Extract file data from start parameter
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except IndexError:
            return
        
        try:
            string = await decode(base64_string)
            argument = string.split("-")
            
            if len(argument) == 3:
                # Batch file handling
                try:
                    start = int(int(argument[1]) / abs(client.db_channel.id))
                    end = int(int(argument[2]) / abs(client.db_channel.id))
                    ids = range(start, end+1) if start <= end else []
                except (ValueError, ZeroDivisionError):
                    return
                
                if len(ids) == 0:
                    return
                
                temp_msg = await message.reply("⏳ Please wait...")
                
                messages = await get_messages(client, ids)
                await temp_msg.delete()

                for msg in messages:
                    if FILE_AUTO_DELETE:
                        caption = f"{getattr(msg, 'caption', '') or ''}\n\n<b>⚠️ This file will be deleted in {get_exp_time(FILE_AUTO_DELETE)}.</b>"
                    else:
                        caption = getattr(msg, 'caption', '') or ''

                    if CUSTOM_CAPTION and hasattr(msg, ('document', 'video', 'audio')):
                        caption = CUSTOM_CAPTION.format(previouscaption="" if not getattr(msg, 'caption', None) else msg.caption.html, filename=get_name(msg))

                    try:
                        copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, protect_content=PROTECT_CONTENT, reply_markup=msg.reply_markup)
                        
                        if FILE_AUTO_DELETE:
                            asyncio.create_task(delete_file_after_delay(client, copied_msg, FILE_AUTO_DELETE))
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
                        copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, protect_content=PROTECT_CONTENT, reply_markup=msg.reply_markup)
                        
                        if FILE_AUTO_DELETE:
                            asyncio.create_task(delete_file_after_delay(client, copied_msg, FILE_AUTO_DELETE))
                    except Exception as e:
                        print(f"Error copying message: {e}")
                        continue
                        
                return

            elif len(argument) == 2:
                # Single file handling
                try:
                    file_id = int(int(argument[1]) / abs(client.db_channel.id)
                except (ValueError, ZeroDivisionError):
                    return
                
                temp_msg = await message.reply("⏳ Please wait...")
                try:
                    msg = await client.get_messages(client.db_channel.id, file_id)
                    
                    if FILE_AUTO_DELETE:
                        caption = f"{getattr(msg, 'caption', '') or ''}\n\n<b>⚠️ This file will be deleted in {get_exp_time(FILE_AUTO_DELETE)}.</b>"
                    else:
                        caption = getattr(msg, 'caption', '') or ''

                    if CUSTOM_CAPTION and hasattr(msg, ('document', 'video', 'audio')):
                        caption = CUSTOM_CAPTION.format(previouscaption="" if not getattr(msg, 'caption', None) else msg.caption.html, filename=get_name(msg))

                    await temp_msg.delete()
                    
                    copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, protect_content=PROTECT_CONTENT, reply_markup=msg.reply_markup)
                    
                    if FILE_AUTO_DELETE:
                        asyncio.create_task(delete_file_after_delay(client, copied_msg, FILE_AUTO_DELETE))
                        
                except Exception as e:
                    await temp_msg.edit(f"❌ Error: {str(e)}")
                    return
                    
                return
        except Exception as e:
            print(f"Error processing file request: {e}")
            return

    # Regular start message
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("ʜᴇʟᴘ", callback_data='help'),
         InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data='about')]
    ])

    if START_PIC:
        try:
            await message.reply_photo(
                photo=START_PIC,
                caption=START_MSG.format(first=message.from_user.first_name),
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML,
                quote=True
            )
        except Exception:
            await message.reply_text(
                text=START_MSG.format(first=message.from_user.first_name),
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=ParseMode.HTML,
                quote=True
            )
    else:
        await message.reply_text(
            text=START_MSG.format(first=message.from_user.first_name),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
            quote=True
        )

# Helper function to get messages
async def get_messages(client, ids):
    messages = []
    for msg_id in ids:
        try:
            msg = await client.get_messages(client.db_channel.id, msg_id)
            messages.append(msg)
        except:
            pass
    return messages

# Helper function to delete files after delay
async def delete_file_after_delay(client, message, delay):
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}")

#=====================================================================================##

# Create a global dictionary to store chat data
chat_data_cache = {}

async def not_joined(client: Client, message: Message):
    temp = await message.reply("<b><i>Checking Subscription...</i></b>")

    user_id = message.from_user.id
    buttons = []
    count = 0

    try:
        all_channels = await db.show_channels()
        for total, chat_id in enumerate(all_channels, start=1):
            mode = await db.get_channel_mode(chat_id)

            await message.reply_chat_action(ChatAction.TYPING)

            if not await is_sub(client, user_id, chat_id):
                try:
                    # Cache chat info
                    if chat_id in chat_data_cache:
                        data = chat_data_cache[chat_id]
                    else:
                        data = await client.get_chat(chat_id)
                        chat_data_cache[chat_id] = data

                    name = data.title

                    # Try to get existing invite link first
                    link = await db.get_invite_link(chat_id)
                    
                    # If no valid link exists, create a new one
                    if not link:
                        if mode == "on" and not data.username:
                            invite = await client.create_chat_invite_link(
                                chat_id=chat_id,
                                creates_join_request=True,
                                expire_date=None
                            )
                            link = invite.invite_link
                            # Store the new link
                            await db.store_invite_link(chat_id, link)
                        else:
                            if data.username:
                                link = f"https://t.me/{data.username}"
                            else:
                                invite = await client.create_chat_invite_link(
                                    chat_id=chat_id,
                                    expire_date=None
                                )
                                link = invite.invite_link
                                # Store the new link
                                await db.store_invite_link(chat_id, link)

                    buttons.append([InlineKeyboardButton(text=name, url=link)])
                    count += 1
                    await temp.edit(f"<b>{'! ' * count}</b>")

                except Exception as e:
                    print(f"Error with chat {chat_id}: {e}")
                    return await temp.edit(
                        f"<b>! Eʀʀᴏʀ</b>\n"
                        f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
                    )

        # Retry Button
        try:
            buttons.append([
                InlineKeyboardButton(
                    text='♻️ Tʀʏ Aɢᴀɪɴ',
                    url=f"https://t.me/{client.username}?start={message.command[1]}" if message.command and len(message.command) > 1 else f"https://t.me/{client.username}"
                )
            ])
        except IndexError:
            pass

        await message.reply_photo(
            photo=FORCE_PIC,
            caption=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    except Exception as e:
        print(f"Final Error: {e}")
        await temp.edit(
            f"<b>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @Authorise_Miko</b>\n"
            f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
        )

#=====================================================================================##

@Bot.on_message(filters.command('myplan') & filters.private)
async def check_plan(client: Client, message: Message):
    user_id = message.from_user.id
    
    try:
        is_premium = await is_premium_user(user_id)
        
        if is_premium:
            # Get premium user details
            user_data = await get_premium_user_data(user_id)
            if user_data:
                expiry_date = user_data.get("expiration_timestamp", "Unknown")
                status_message = f"<b>✅ Premium Status: Active</b>\n\n<b>Expires:</b> {expiry_date}"
            else:
                status_message = "<b>✅ Premium Status: Active</b>\n\n<b>Expires:</b> Unknown"
        else:
            status_message = "<b>❌ Premium Status: Not Active</b>\n\n<i>Contact @Yae_X_Miko to purchase premium.</i>"
            
    except Exception as e:
        status_message = f"<b>❌ Error checking premium status:</b>\n<code>{str(e)}</code>"
    
    # Ensure message is not empty
    if not status_message or status_message.strip() == "":
        status_message = "<b>❌ Unable to retrieve plan status. Please contact support.</b>"
    
    await message.reply(status_message)

#=====================================================================================##
# Command to add premium user
@Bot.on_message(filters.command('addpremium') & filters.private & admin)
async def add_premium_user_command(client, msg):
    if len(msg.command) != 4:
        await msg.reply_text(
            "Usage: /addpremium <user_id> <time_value> <time_unit>\n\n"
            "Time Units:\n"
            "s - seconds\n"
            "m - minutes\n"
            "h - hours\n"
            "d - days\n"
            "y - years\n\n"
            "Examples:\n"
            "/addpremium 123456789 30 m → 30 minutes\n"
            "/addpremium 123456789 2 h → 2 hours\n"
            "/addpremium 123456789 1 d → 1 day\n"
            "/addpremium 123456789 1 y → 1 year"
        )
        return

    try:
        user_id = int(msg.command[1])
        time_value = int(msg.command[2])
        time_unit = msg.command[3].lower()  # supports: s, m, h, d, y

        # Call add_premium function
        expiration_time = await add_premium(user_id, time_value, time_unit)

        # Notify the admin
        await msg.reply_text(
            f"✅ User `{user_id}` added as a premium user for {time_value} {time_unit}.\n"
            f"Expiration Time: `{expiration_time}`"
        )

        # Notify the user
        await client.send_message(
            chat_id=user_id,
            text=(
                f"🎉 Premium Activated!\n\n"
                f"You have received premium access for `{time_value} {time_unit}`.\n"
                f"Expires on: `{expiration_time}`"
            ),
        )

    except ValueError:
        await msg.reply_text("❌ Invalid input. Please ensure user ID and time value are numbers.")
    except Exception as e:
        await msg.reply_text(f"⚠️ An error occurred: `{str(e)}`")

# Command to remove premium user
@Bot.on_message(filters.command('remove_premium') & filters.private & admin)
async def pre_remove_user(client: Client, msg: Message):
    if len(msg.command) != 2:
        await msg.reply_text("Usage: /remove_premium user_id")
        return
    try:
        user_id = int(msg.command[1])
        await remove_premium(user_id)
        await msg.reply_text(f"User {user_id} has been removed.")
    except ValueError:
        await msg.reply_text("user_id must be an integer or not available in database.")

# Command to list active premium users
@Bot.on_message(filters.command('premium_users') & filters.private & admin)
async def list_premium_users_command(client, message):
    # Define IST timezone
    ist = timezone("Asia/Kolkata")

    # Retrieve all users from the collection
    premium_users_cursor = collection.find({})
    premium_user_list = ['Active Premium Users in database:']
    current_time = datetime.now(ist)  # Get current time in IST

    # Use async for to iterate over the async cursor
    async for user in premium_users_cursor:
        user_id = user["user_id"]
        expiration_timestamp = user["expiration_timestamp"]

        try:
            # Convert expiration_timestamp to a timezone-aware datetime object in IST
            expiration_time = datetime.fromisoformat(expiration_timestamp).astimezone(ist)

            # Calculate remaining time
            remaining_time = expiration_time - current_time

            if remaining_time.total_seconds() <= 0:
                # Remove expired users from the database
                await collection.delete_one({"user_id": user_id})
                continue  # Skip to the next user if this one is expired

            # If not expired, retrieve user info
            user_info = await client.get_users(user_id)
            username = user_info.username if user_info.username else "No Username"
            first_name = user_info.first_name
            mention = user_info.mention

            # Calculate days, hours, minutes, seconds left
            days, hours, minutes, seconds = (
                remaining_time.days,
                remaining_time.seconds // 3600,
                (remaining_time.seconds // 60) % 60,
                remaining_time.seconds % 60,
            )
            expiry_info = f"{days}d {hours}h {minutes}m {seconds}s left"

            # Add user details to the list
            premium_user_list.append(
                f"UserID: <code>{user_id}</code>\n"
                f"User: @{username}\n"
                f"Name: {mention}\n"
                f"Expiry: {expiry_info}"
            )
        except Exception as e:
            premium_user_list.append(
                f"UserID: <code>{user_id}</code>\n"
                f"Error: Unable to fetch user details ({str(e)})"
            )

    if len(premium_user_list) == 1:  # No active users found
        await message.reply_text("I found 0 active premium users in my DB")
    else:
        await message.reply_text("\n\n".join(premium_user_list), parse_mode=None)

#=====================================================================================##

@Bot.on_message(filters.command("count") & filters.private & admin)
async def total_verify_count_cmd(client, message: Message):
    total = await db.get_total_verify_count()
    await message.reply_text(f"Tᴏᴛᴀʟ ᴠɪғɪᴇᴇᴅ ᴛᴏᴋᴇɴs ᴛᴏᴅᴀʏ: <b>{total}</b>")

#=====================================================================================##

@Bot.on_message(filters.command('commands') & filters.private & admin)
async def bcmd(bot: Bot, message: Message):        
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data = "close")]])
    await message.reply(text=CMD_TXT, reply_markup = reply_markup, quote= True)

#=====================================================================================##

@Bot.on_callback_query(filters.regex("reload"))
async def reload_btn(client, query):
    if await is_subscribed(client, query.from_user.id):
        await query.message.delete()
        return await query.message.reply("/start", quote=True)
    await query.answer("❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ sᴜʙsᴄʀɪʙᴇᴅ ᴛᴏ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ!", show_alert=True)

#=====================================================================================##
