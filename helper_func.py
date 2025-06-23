#(©)CodeFlix_Bots
#rohit_1888 on Tg #Dont remove this line

import base64
import re
import asyncio
import time
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from config import *
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from shortzy import Shortzy
from pyrogram.errors import FloodWait
from database.database import *
from database.db_premium import *
import logging

# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport
#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

#used for cheking if a user is admin ~Owner also treated as admin level
async def check_admin(filter, client, update):
    try:
        user_id = update.from_user.id       
        return any([user_id == OWNER_ID, await db.admin_exist(user_id)])
    except Exception as e:
        print(f"! Exception in check_admin: {e}")
        return False

# Enhanced premium checking with automatic cleanup
async def is_premium_user_enhanced(user_id):
    """Enhanced premium check with automatic expiry cleanup"""
    try:
        # First check if user exists in premium collection
        user_exists = await is_premium_user(user_id)
        if not user_exists:
            return False
        
        # Check if premium has expired and auto-remove
        user_data = await collection.find_one({"user_id": user_id})
        if user_data:
            from datetime import datetime
            from pytz import timezone
            
            ist = timezone("Asia/Kolkata")
            current_time = datetime.now(ist)
            expiration_time = datetime.fromisoformat(user_data["expiration_timestamp"]).astimezone(ist)
            
            if expiration_time <= current_time:
                # Auto remove expired user
                await remove_premium(user_id)
                logging.info(f"Auto-removed expired premium user: {user_id}")
                return False
        
        return True
    except Exception as e:
        logging.error(f"Error in enhanced premium check for user {user_id}: {e}")
        return False

# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport
#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

async def is_subscribed(client, user_id):
    channel_ids = await db.show_channels()

    if not channel_ids:
        return True

    if user_id == OWNER_ID:
        return True

    for cid in channel_ids:
        if not await is_sub(client, user_id, cid):
            # Retry once if join request might be processing
            mode = await db.get_channel_mode(cid)
            if mode == "on":
                await asyncio.sleep(2)  # give time for @on_chat_join_request to process
                if await is_sub(client, user_id, cid):
                    continue
            return False

    return True

# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport
#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

async def is_sub(client, user_id, channel_id):
    try:
        member = await client.get_chat_member(channel_id, user_id)
        status = member.status
        #print(f"[SUB] User {user_id} in {channel_id} with status {status}")
        return status in {
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.MEMBER
        }

    except UserNotParticipant:
        mode = await db.get_channel_mode(channel_id)
        if mode == "on":
            exists = await db.req_user_exist(channel_id, user_id)
            #print(f"[REQ] User {user_id} join request for {channel_id}: {exists}")
            return exists
        #print(f"[NOT SUB] User {user_id} not in {channel_id} and mode != on")
        return False

    except Exception as e:
        print(f"[!] Error in is_sub(): {e}")
        return False

# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport
#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

async def not_joined(client, message):
    channels = await db.show_channels()
    channel_names = []
    buttons = []

    for channel_id in channels:
        try:
            mode = await db.get_channel_mode(channel_id)
            chat = await client.get_chat(channel_id)
            invite_link = chat.invite_link

            if not invite_link:
                invite_link = await client.export_chat_invite_link(channel_id)

            channel_names.append(chat.title)
            button_text = "ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ" if mode == "on" else "ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ"
            buttons.append([InlineKeyboardButton(text=button_text, url=invite_link)])
        except Exception as e:
            print(f"Error processing channel {channel_id}: {e}")

    try:
        buttons.append([InlineKeyboardButton(text='ʀᴇʟᴏᴀᴅ', callback_data='reload')])

        # Construct the joined channel names text
        if len(channel_names) > 1:
            joined_channels = ", ".join(channel_names[:-1]) + f" ᴀɴᴅ {channel_names[-1]}"
        else:
            joined_channels = channel_names[0] if channel_names else "our channels"

        await message.reply_photo(
            photo=FORCE_PIC,
            caption=FORCE_MSG.format(first=message.from_user.first_name, joined_channels=joined_channels),
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
        
    except Exception as e:
        print(f"Error sending force subscription message: {e}")

# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport
#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

admin = filters.create(check_admin)

async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.b64encode(string_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string

async def decode(base64_string):
    base64_bytes = base64_string.encode("ascii")
    string_bytes = base64.b64decode(base64_bytes)
    string = string_bytes.decode("ascii")
    return string

async def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        else:
            return 0
    elif message.forward_from:
        return 0
    elif message.text:
        pattern = "https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern, message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        else:
            if channel_id == client.db_channel.username:
                return msg_id
    else:
        return 0

def get_readable_time(seconds):
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for i in range(hmm):
        time_list[i] = str(time_list[i]) + time_suffix_list[i]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time

def get_exp_time(seconds):
    periods = [('days', 86400), ('hours', 3600), ('minutes', 60), ('seconds', 1)]
    result = []
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result.append(f"{period_value} {period_name}")
    return ', '.join(result)

# FIXED SHORTENER ROTATION SYSTEM
async def get_shortlink_rotated(user_id, original_link):
    """Enhanced shortener rotation with proper cycle tracking"""
    try:
        # Get current shortener status for user
        user_status = await get_user_shortener_status(user_id)
        
        # Check if user has already used this shortener in current cycle
        current_shortener_index = user_status['next_shortener']
        used_shorteners = user_status.get('used_shorteners', [])
        
        # If current shortener was already used, find next unused one
        if current_shortener_index in used_shorteners:
            # Find next unused shortener
            for i in range(len(SHORTLINK_URLS)):
                if i not in used_shorteners:
                    current_shortener_index = i
                    break
            else:
                # All shorteners used, reset cycle
                used_shorteners = []
                current_shortener_index = 0
        
        # Update user's shortener tracking
        await update_user_shortener_tracking(user_id, current_shortener_index, used_shorteners)
        
        # Create short link with current shortener
        shortener = Shortzy(api=SHORTLINK_APIS[current_shortener_index], url=SHORTLINK_URLS[current_shortener_index])
        short_link = await shortener.convert(original_link)
        
        return short_link
        
    except Exception as e:
        logging.error(f"Error in shortener rotation for user {user_id}: {e}")
        # Fallback to first shortener
        try:
            shortener = Shortzy(api=SHORTLINK_APIS[0], url=SHORTLINK_URLS[0])
            return await shortener.convert(original_link)
        except:
            return original_link

async def get_user_shortener_status(user_id):
    """Get user's current shortener rotation status"""
    try:
        user_data = await db.get_verify_status(user_id)
        shortener_data = user_data.get('shortener_data', {})
        
        return {
            'next_shortener': shortener_data.get('next_shortener', 0),
            'used_shorteners': shortener_data.get('used_shorteners', []),
            'cycle_complete': shortener_data.get('cycle_complete', False),
            'shortener_names': [url.replace('https://', '').replace('http://', '') for url in SHORTLINK_URLS]
        }
    except Exception as e:
        logging.error(f"Error getting shortener status for user {user_id}: {e}")
        return {
            'next_shortener': 0,
            'used_shorteners': [],
            'cycle_complete': False,
            'shortener_names': [url.replace('https://', '').replace('http://', '') for url in SHORTLINK_URLS]
        }

async def update_user_shortener_tracking(user_id, used_shortener_index, used_shorteners):
    """Update user's shortener tracking data"""
    try:
        # Add current shortener to used list if not already there
        if used_shortener_index not in used_shorteners:
            used_shorteners.append(used_shortener_index)
        
        # Calculate next shortener index
        next_shortener = (used_shortener_index + 1) % len(SHORTLINK_URLS)
        
        # Check if cycle is complete
        cycle_complete = len(used_shorteners) >= len(SHORTLINK_URLS)
        
        # If cycle complete, reset for next cycle
        if cycle_complete:
            used_shorteners = []
            next_shortener = 0
        
        # Update database
        await db.update_user_shortener_data(user_id, {
            'next_shortener': next_shortener,
            'used_shorteners': used_shorteners,
            'cycle_complete': cycle_complete,
            'last_updated': time.time()
        })
        
    except Exception as e:
        logging.error(f"Error updating shortener tracking for user {user_id}: {e}")

async def reset_user_shortener_cycle(user_id):
    """Reset user's shortener cycle - for admin use"""
    try:
        await db.update_user_shortener_data(user_id, {
            'next_shortener': 0,
            'used_shorteners': [],
            'cycle_complete': False,
            'last_updated': time.time()
        })
        return True
    except Exception as e:
        logging.error(f"Error resetting shortener cycle for user {user_id}: {e}")
        return False

# Legacy shortener function for backward compatibility
async def get_shortlink(url, api):
    try:
        shortener = Shortzy(api=api, url=url)
        link = await shortener.convert(url)
        return link
    except Exception as e:
        logging.error(f"Error creating shortlink: {e}")
        return url

# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport
#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#
