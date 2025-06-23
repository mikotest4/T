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

admin = filters.create(check_admin, "AdminFilter")

def get_readable_time(seconds: int) -> str:
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
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time

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
    elif message.forward_sender_name:
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
        elif channel_id == client.db_channel.username:
            return msg_id
    else:
        return 0

def get_name(media):
    return getattr(media, 'file_name', 'None')

def get_media_file_size(m):
    media = getattr(m, m.content_type.replace('_', ''), None)
    if not media:
        return 0
    return media.file_size

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def get_exp_time(seconds):
    periods = [('d', 86400), ('h', 3600), ('m', 60), ('s', 1)]
    result = []
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result.append(f"{int(period_value)}{period_name}")
    return " ".join(result) if result else "0s"

# SMART SHORTENER ROTATION SYSTEM
async def get_shortlink_rotated(user_id, original_url):
    """Get shortlink using rotation system"""
    from config import SHORTLINK_URLS, SHORTLINK_APIS
    
    if not SHORTLINK_URLS or not SHORTLINK_APIS:
        return original_url
    
    # Ensure both lists have the same length
    if len(SHORTLINK_URLS) != len(SHORTLINK_APIS):
        logging.error("SHORTLINK_URLS and SHORTLINK_APIS must have the same length")
        return original_url
    
    # Get next shortener for this user
    shortener_index = await db.get_next_shortener_for_user(user_id, len(SHORTLINK_URLS))
    
    # Get the shortener details
    shortlink_url = SHORTLINK_URLS[shortener_index]
    shortlink_api = SHORTLINK_APIS[shortener_index]
    
    try:
        # Generate shortlink
        shortzy = Shortzy(api_key=shortlink_api, base_site=shortlink_url)
        link = await shortzy.convert(original_url)
        
        # Update user's shortener history
        await db.update_user_shortener_history(user_id, shortener_index)
        
        logging.info(f"Generated shortlink for user {user_id} using shortener {shortener_index} ({shortlink_url})")
        return link
    except Exception as e:
        logging.error(f"Error generating shortlink with index {shortener_index} ({shortlink_url}): {e}")
        return original_url

async def get_user_shortener_status(user_id):
    """Get user's current shortener rotation status"""
    from config import SHORTLINK_URLS
    
    history = await db.get_user_shortener_history(user_id)
    used_indices = set(item['index'] for item in history)
    
    status = {
        'total_shorteners': len(SHORTLINK_URLS),
        'used_count': len(used_indices),
        'next_shortener': await db.get_next_shortener_for_user(user_id, len(SHORTLINK_URLS)),
        'cycle_complete': len(used_indices) >= len(SHORTLINK_URLS),
        'shortener_names': SHORTLINK_URLS
    }
    
    return status

# Legacy shortlink function for backward compatibility
async def get_shortlink(SHORTLINK_URL, SHORTLINK_API, link):
    """Legacy shortlink function - now uses rotation system"""
    return link  # Original implementation maintained for compatibility

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
    buttons = []
    try:
        channel_ids = await db.show_channels()
        for channel_id in channel_ids:
            try:
                chat = await client.get_chat(channel_id)
                
                # Check for invite link
                if chat.invite_link:
                    link = chat.invite_link
                elif chat.username:
                    link = f"https://t.me/{chat.username}"
                else:
                    try:
                        link = await client.export_chat_invite_link(channel_id)
                    except Exception as e:
                        print(f"Error creating invite link for {channel_id}: {e}")
                        link = f"https://t.me/c/{str(channel_id)[4:]}"
                
                # Check mode for join request handling
                mode = await db.get_channel_mode(channel_id)
                if mode == "on":
                    # Add channel to request tracking
                    await db.add_reqChannel(channel_id)
                    buttons.append([InlineKeyboardButton(f"📢 ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ - {chat.title}", url=link)])
                else:
                    buttons.append([InlineKeyboardButton(f"📢 ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ - {chat.title}", url=
