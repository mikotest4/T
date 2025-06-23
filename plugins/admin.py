import asyncio
import os
import random
import sys
import time
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction, ChatMemberStatus, ChatType
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatMemberUpdated, ChatPermissions
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, InviteHashEmpty, ChatAdminRequired, PeerIdInvalid, UserIsBlocked, InputUserDeactivated
from bot import Bot
from config import *
from helper_func import *
from database.database import *



# Commands for adding admins by owner
@Bot.on_message(filters.command('add_admin') & filters.private & filters.user(OWNER_ID))
async def add_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    check = 0
    admin_ids = await db.get_all_admins()
    admins = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    if not admins:
        return await pro.edit(
            "<b>You need to provide user ID(s) to add as admin.</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>/add_admin [user_id]</code> — Add one or more user IDs\n\n"
            "<b>Example:</b>\n"
            "<code>/add_admin 1234567890 9876543210</code>",
            reply_markup=reply_markup
        )

    admin_list = ""
    for id in admins:
        try:
            id = int(id)
        except:
            admin_list += f"<blockquote><b>Invalid ID: <code>{id}</code></b></blockquote>\n"
            continue

        if id in admin_ids:
            admin_list += f"<blockquote><b>ID <code>{id}</code> already exists.</b></blockquote>\n"
            continue

        id = str(id)
        if id.isdigit() and len(id) == 10:
            admin_list += f"<b><blockquote>(ID: <code>{id}</code>) added.</blockquote></b>\n"
            check += 1
        else:
            admin_list += f"<blockquote><b>Invalid ID: <code>{id}</code></b></blockquote>\n"

    if check == len(admins):
        for id in admins:
            await db.add_admin(int(id))
        await pro.edit(f"<b>✅ Admin(s) added successfully:</b>\n\n{admin_list}", reply_markup=reply_markup)
    else:
        await pro.edit(
            f"<b>❌ Some errors occurred while adding admins:</b>\n\n{admin_list.strip()}\n\n"
            "<b><i>Please check and try again.</i></b>",
            reply_markup=reply_markup
        )

@Bot.on_message(filters.command('deladmin') & filters.private & filters.user(OWNER_ID))
async def delete_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    admin_ids = await db.get_all_admins()
    admins = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    if not admins:
        return await pro.edit(
            "<b>Please provide valid admin ID(s) to remove.</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>/deladmin [user_id]</code> — Remove specific IDs\n"
            "<code>/deladmin all</code> — Remove all admins",
            reply_markup=reply_markup
        )

    if len(admins) == 1 and admins[0].lower() == "all":
        if admin_ids:
            for id in admin_ids:
                await db.del_admin(id)
            ids = "\n".join(f"<blockquote><code>{admin}</code> ✅</blockquote>" for admin in admin_ids)
            return await pro.edit(f"<b>⛔️ All admin IDs have been removed:</b>\n{ids}", reply_markup=reply_markup)
        else:
            return await pro.edit("<b><blockquote>No admin IDs to remove.</blockquote></b>", reply_markup=reply_markup)

    if admin_ids:
        passed = ''
        for admin_id in admins:
            try:
                id = int(admin_id)
            except:
                passed += f"<blockquote><b>Invalid ID: <code>{admin_id}</code></b></blockquote>\n"
                continue

            if id in admin_ids:
                await db.del_admin(id)
                passed += f"<blockquote><code>{id}</code> ✅ Removed</blockquote>\n"
            else:
                passed += f"<blockquote><b>ID <code>{id}</code> not found in admin list.</b></blockquote>\n"

        await pro.edit(f"<b>⛔️ Admin removal result:</b>\n\n{passed}", reply_markup=reply_markup)
    else:
        await pro.edit("<b><blockquote>No admin IDs available to delete.</blockquote></b>", reply_markup=reply_markup)


@Bot.on_message(filters.command('admins') & filters.private & admin)
async def get_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    admin_ids = await db.get_all_admins()

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    if not admin_ids:
        return await pro.edit("<b><blockquote>No admin IDs found.</blockquote></b>", reply_markup=reply_markup)

    admin_list = "<b>👑 ᴀᴠᴀɪʟᴀʙʟᴇ ᴀᴅᴍɪɴs:</b>\n\n"
    for i, admin_id in enumerate(admin_ids, 1):
        try:
            user = await client.get_users(admin_id)
            name = user.first_name or "Unknown"
            username = f"@{user.username}" if user.username else "No username"
            admin_list += f"<b>{i}.</b> <a href='tg://user?id={admin_id}'>{name}</a> ({username})\n"
            admin_list += f"   └ <code>{admin_id}</code>\n\n"
        except:
            admin_list += f"<b>{i}.</b> <code>{admin_id}</code> (Unable to fetch details)\n\n"

    await pro.edit(admin_list, reply_markup=reply_markup, disable_web_page_preview=True)

# Shortener Rotation Statistics
@Bot.on_message(filters.command('rotation_stats') & admin & filters.private)
async def rotation_statistics(client: Bot, message: Message):
    """Show shortener rotation statistics"""
    from config import SHORTLINK_URLS, SHORTLINK_APIS
    
    try:
        pro = await message.reply("📊 <i>Fetching rotation statistics...</i>", quote=True)
        
        if not SHORTLINK_URLS or not SHORTLINK_APIS:
            return await pro.edit(
                "<b>❌ No shorteners configured</b>\n\n"
                "Please configure SHORTLINK_URLS and SHORTLINK_APIS in your environment variables."
            )
        
        # Get all users
        all_users = await db.full_userbase()
        
        stats = {
            'total_users': len(all_users),
            'users_in_cycle': 0,
            'completed_cycles': 0,
            'shortener_usage': {i: 0 for i in range(len(SHORTLINK_URLS))}
        }
        
        # Process users (limit to avoid timeout)
        processed_count = 0
        for user_id in all_users[:500]:  # Limit to first 500 for performance
            try:
                history = await db.get_user_shortener_history(user_id)
                if history:
                    stats['users_in_cycle'] += 1
                    used_indices = set(item['index'] for item in history)
                    
                    if len(used_indices) >= len(SHORTLINK_URLS):
                        stats['completed_cycles'] += 1
                    
                    for item in history:
                        if item['index'] in stats['shortener_usage']:
                            stats['shortener_usage'][item['index']] += 1
                
                processed_count += 1
            except:
                continue
        
        # Format response
        response = f"🔄 <b>Shortener Rotation Statistics</b>\n\n"
        response += f"👥 Total Users: {stats['total_users']}\n"
        response += f"📊 Processed: {processed_count}\n"
        response += f"🔄 Users in Rotation: {stats['users_in_cycle']}\n"
        response += f"✅ Completed Cycles: {stats['completed_cycles']}\n\n"
        response += f"📊 <b>Shortener Usage:</b>\n"
        
        for i, url in enumerate(SHORTLINK_URLS):
            usage_count = stats['shortener_usage'].get(i, 0)
            api_configured = "✅" if i < len(SHORTLINK_APIS) and SHORTLINK_APIS[i] != "your_api_key_here" else "❌"
            response += f"{i+1}. {url} {api_configured}\n   └ Uses: {usage_count}\n\n"
        
        response += f"\n⏱️ <i>Verification Time: {get_exp_time(VERIFY_EXPIRE)} per shortener</i>"
        
        await pro.edit(
            response,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")
            ]])
        )
        
    except Exception as e:
        await message.reply(f"❌ Error getting rotation stats: {str(e)}")

@Bot.on_message(filters.command('reset_rotation') & admin & filters.private)
async def reset_user_rotation(client: Bot, message: Message):
    """Reset rotation for specific user"""
    try:
        if len(message.command) < 2:
            return await message.reply(
                "<b>Usage:</b> <code>/reset_rotation [user_id]</code>\n\n"
                "<b>Example:</b> <code>/reset_rotation 1234567890</code>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")
                ]])
            )
        
        user_id = int(message.command[1])
        
        # Check if user exists
        if not await db.present_user(user_id):
            return await message.reply(
                f"❌ User {user_id} not found in database.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")
                ]])
            )
        
        # Reset the cycle
        await db.reset_user_shortener_cycle(user_id)
        
        await message.reply(
            f"✅ <b>Reset Complete</b>\n\n"
            f"Shortener rotation cycle has been reset for user: <code>{user_id}</code>\n\n"
            f"The user will start from the first shortener on their next verification.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")
            ]])
        )
        
    except ValueError:
        await message.reply(
            "❌ <b>Invalid User ID</b>\n\n"
            "Please provide a valid numeric user ID.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")
            ]])
        )
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

@Bot.on_message(filters.command('shortener_config') & admin & filters.private)
async def shortener_config(client: Bot, message: Message):
    """Show current shortener configuration"""
    from config import SHORTLINK_URLS, SHORTLINK_APIS, VERIFY_EXPIRE
    
    try:
        response = f"⚙️ <b>Shortener Configuration</b>\n\n"
        response += f"⏱️ <b>Verification Time:</b> {get_exp_time(VERIFY_EXPIRE)} per shortener\n\n"
        
        if not SHORTLINK_URLS:
            response += "❌ <b>No shorteners configured</b>"
        else:
            response += f"📊 <b>Configured Shorteners:</b> {len(SHORTLINK_URLS)}\n\n"
            
            for i, url in enumerate(SHORTLINK_URLS):
                api_status = "✅ Configured" if i < len(SHORTLINK_APIS) and SHORTLINK_APIS[i] != "your_api_key_here" else "❌ Not configured"
                response += f"{i+1}. <b>{url}</b>\n   └ API: {api_status}\n\n"
            
            total_time = len(SHORTLINK_URLS) * VERIFY_EXPIRE
            response += f"🎯 <b>Total cycle time:</b> {get_exp_time(total_time)}"
        
        await message.reply(
            response,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 Rotation Stats", callback_data="get_rotation_stats"),
                InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")
            ]])
        )
        
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

# Handle callback for rotation stats
@Bot.on_callback_query(filters.regex("get_rotation_stats"))
async def get_rotation_stats_callback(client: Bot, callback_query: CallbackQuery):
    """Handle rotation stats callback"""
    await callback_query.answer()
    # Create a fake message to reuse the rotation_statistics function
    fake_message = callback_query.message
    fake_message.command = ['rotation_stats']
    await rotation_statistics(client, fake_message)
