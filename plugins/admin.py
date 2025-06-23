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
    try:
        admins = await db.get_all_admins()
        
        if not admins:
            return await message.reply(
                "<b>👤 Current Admins:</b>\n\n"
                f"<blockquote>👑 Owner: <code>{OWNER_ID}</code></blockquote>\n"
                "<blockquote>ℹ️ No additional admins found.</blockquote>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cʟᴏsᴇ", callback_data="close")]])
            )
        
        admin_list = f"<b>👤 Current Admins ({len(admins) + 1}):</b>\n\n"
        admin_list += f"<blockquote>👑 Owner: <code>{OWNER_ID}</code></blockquote>\n"
        
        for admin_id in admins:
            try:
                user = await client.get_users(admin_id)
                name = user.first_name if user.first_name else "Unknown"
                username = f"@{user.username}" if user.username else "No username"
                admin_list += f"<blockquote>👤 <b>{name}</b> (<code>{admin_id}</code>) - {username}</blockquote>\n"
            except Exception:
                admin_list += f"<blockquote>👤 <code>{admin_id}</code> - <i>User info not accessible</i></blockquote>\n"
        
        await message.reply(
            admin_list,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cʟᴏsᴇ", callback_data="close")]])
        )
        
    except Exception as e:
        await message.reply(f"❌ Error retrieving admins: {str(e)}")

# SHORTENER ROTATION SYSTEM ADMIN COMMANDS
@Bot.on_message(filters.command('rotation_stats') & admin & filters.private)
async def rotation_statistics(client: Bot, message: Message):
    """Show shortener rotation statistics"""
    from config import SHORTLINK_URLS, SHORTLINK_APIS
    
    try:
        if not SHORTLINK_URLS or not SHORTLINK_APIS:
            return await message.reply("❌ No shorteners configured.")
        
        # Get all users
        all_users = await db.full_userbase()
        
        stats = {
            'total_users': len(all_users),
            'users_in_cycle': 0,
            'completed_cycles': 0,
            'shortener_usage': {i: 0 for i in range(len(SHORTLINK_URLS))}
        }
        
        # Analyze first 500 users for performance
        sample_users = all_users[:500]
        
        for user_id in sample_users:
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
            except:
                continue
        
        # Get database shortener usage stats
        db_stats = await db.get_shortener_usage_stats(1000)
        
        # Format response
        response = f"🔄 <b>Shortener Rotation Statistics</b>\n\n"
        response += f"👥 Total Users: {stats['total_users']}\n"
        response += f"🔄 Users in Rotation (sample): {stats['users_in_cycle']}/{len(sample_users)}\n"
        response += f"✅ Completed Cycles: {stats['completed_cycles']}\n\n"
        response += f"📊 <b>Shortener Configuration:</b>\n"
        
        for i, url in enumerate(SHORTLINK_URLS):
            sample_usage = stats['shortener_usage'].get(i, 0)
            db_usage = next((stat['usage_count'] for stat in db_stats if stat['shortener_index'] == i), 0)
            response += f"{i+1}. {url}\n"
            response += f"   📈 Sample Usage: {sample_usage}\n"
            response += f"   💾 DB Usage: {db_usage}\n\n"
        
        response += f"⚠️ <i>Sample shows first {len(sample_users)} users only</i>"
        
        await message.reply(response, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Close", callback_data="close")]]))
        
    except Exception as e:
        await message.reply(f"❌ Error getting rotation stats: {str(e)}")

@Bot.on_message(filters.command('reset_rotation') & admin & filters.private)
async def reset_user_rotation(client: Bot, message: Message):
    """Reset rotation for specific user"""
    try:
        if len(message.command) < 2:
            return await message.reply(
                "📝 <b>Usage:</b>\n"
                "<code>/reset_rotation [user_id]</code>\n"
                "<code>/reset_rotation all</code> - Reset all users",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Close", callback_data="close")]])
            )
        
        if message.command[1].lower() == "all":
            # Reset all users
            temp_msg = await message.reply("🔄 Resetting rotation for all users...")
            
            try:
                all_users = await db.full_userbase()
                reset_count = 0
                
                for user_id in all_users[:1000]:  # Limit for performance
                    try:
                        await db.reset_user_shortener_cycle(user_id)
                        reset_count += 1
                    except:
                        continue
                
                await temp_msg.edit(
                    f"✅ Reset shortener rotation cycle for {reset_count} users",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Close", callback_data="close")]])
                )
                
            except Exception as e:
                await temp_msg.edit(f"❌ Error during bulk reset: {str(e)}")
        else:
            # Reset specific user
            user_id = int(message.command[1])
            await db.reset_user_shortener_cycle(user_id)
            
            await message.reply(
                f"✅ Reset shortener rotation cycle for user <code>{user_id}</code>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Close", callback_data="close")]])
            )
        
    except ValueError:
        await message.reply(
            "❌ Invalid user ID. Please provide a valid number.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Close", callback_data="close")]])
        )
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

@Bot.on_message(filters.command('check_user_rotation') & admin & filters.private)
async def check_user_rotation_status(client: Bot, message: Message):
    """Check specific user's rotation status"""
    try:
        if len(message.command) < 2:
            return await message.reply(
                "📝 <b>Usage:</b>\n<code>/check_user_rotation [user_id]</code>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Close", callback_data="close")]])
            )
        
        user_id = int(message.command[1])
        
        # Get user's rotation status
        shortener_status = await get_user_shortener_status(user_id)
        history = await db.get_user_shortener_history(user_id)
        
        # Get user info
        try:
            user = await client.get_users(user_id)
            user_name = user.first_name if user.first_name else "Unknown"
        except:
            user_name = "Unknown"
        
        response = f"👤 <b>User Rotation Status</b>\n\n"
        response += f"🆔 User ID: <code>{user_id}</code>\n"
        response += f"👤 Name: {user_name}\n\n"
        response += f"📊 <b>Rotation Info:</b>\n"
        response += f"🔢 Total Shorteners: {shortener_status['total_shorteners']}\n"
        response += f"✅ Used Count: {shortener_status['used_count']}\n"
        response += f"🔄 Cycle Complete: {'Yes' if shortener_status['cycle_complete'] else 'No'}\n"
        
        if not shortener_status['cycle_complete']:
            next_shortener = shortener_status['shortener_names'][shortener_status['next_shortener']]
            response += f"➡️ Next Shortener: {next_shortener}\n"
        
        response += f"\n📜 <b>Usage History:</b>\n"
        if history:
            for item in history[-5:]:  # Show last 5 entries
                shortener_name = shortener_status['shortener_names'][item['index']]
                used_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['used_at']))
                response += f"• {shortener_name} - {used_time}\n"
        else:
            response += "• No usage history found\n"
        
        await message.reply(
            response,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Close", callback_data="close")]])
        )
        
    except ValueError:
        await message.reply("❌ Invalid user ID. Please provide a valid number.")
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

@Bot.on_message(filters.command('shortener_config') & admin & filters.private)
async def show_shortener_config(client: Bot, message: Message):
    """Show current shortener configuration"""
    try:
        from config import SHORTLINK_URLS, SHORTLINK_APIS, VERIFY_EXPIRE
        
        response = f"⚙️ <b>Shortener Configuration</b>\n\n"
        
        if not SHORTLINK_URLS or not SHORTLINK_APIS:
            response += "❌ No shorteners configured\n"
            response += "Please set SHORTLINK_URLS and SHORTLINK_APIS in your environment variables."
        else:
            response += f"🔢 Total Shorteners: {len(SHORTLINK_URLS)}\n"
            response += f"⏰ Verify Expire: {get_exp_time(VERIFY_EXPIRE)} per shortener\n"
            response += f"🔄 Total Cycle Time: {get_exp_time(VERIFY_EXPIRE * len(SHORTLINK_URLS))}\n\n"
            
            response += f"📋 <b>Configured Shorteners:</b>\n"
            for i, url in enumerate(SHORTLINK_URLS):
                api_status = "✅ Set" if i < len(SHORTLINK_APIS) and SHORTLINK_APIS[i] else "❌ Missing"
                response += f"{i+1}. {url} - API: {api_status}\n"
            
            if len(SHORTLINK_URLS) != len(SHORTLINK_APIS):
                response += f"\n⚠️ <b>Warning:</b> URLs ({len(SHORTLINK_URLS)}) and APIs ({len(SHORTLINK_APIS)}) count mismatch!"
        
        await message.reply(
            response,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Close", callback_data="close")]])
        )
        
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")
