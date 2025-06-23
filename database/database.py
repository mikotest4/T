import motor, asyncio
import motor.motor_asyncio
import time
import pymongo, os
from config import DB_URI, DB_NAME
import logging
from datetime import datetime, timedelta

dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

logging.basicConfig(level=logging.INFO)

default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'link': ""
}

def new_user(id):
    return {
        '_id': id,
        'verify_status': {
            'is_verified': False,
            'verified_time': "",
            'verify_token': "",
            'link': ""
        },
        'shortener_history': []
    }

class Yae_X_Miko:

    def __init__(self, DB_URI, DB_NAME):
        self.dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
        self.database = self.dbclient[DB_NAME]

        self.channel_data = self.database['channels']
        self.admins_data = self.database['admins']
        self.user_data = self.database['users']
        self.sex_data = self.database['sex']
        self.banned_user_data = self.database['banned_user']
        self.autho_user_data = self.database['autho_user']
        self.del_timer_data = self.database['del_timer']
        self.fsub_data = self.database['fsub']   
        self.rqst_fsub_data = self.database['request_forcesub']
        self.rqst_fsub_Channel_data = self.database['request_forcesub_channel']
        


    # USER DATA
    async def present_user(self, user_id: int):
        found = await self.user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_user(self, user_id: int):
        await self.user_data.insert_one(new_user(user_id))
        return

    async def full_userbase(self):
        user_docs = await self.user_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in user_docs]
        return user_ids

    async def del_user(self, user_id: int):
        await self.user_data.delete_one({'_id': user_id})
        return


    # ADMIN DATA
    async def admin_exist(self, admin_id: int):
        found = await self.admins_data.find_one({'_id': admin_id})
        return bool(found)

    async def add_admin(self, admin_id: int):
        if not await self.admin_exist(admin_id):
            await self.admins_data.insert_one({'_id': admin_id})
            return

    async def del_admin(self, admin_id: int):
        if await self.admin_exist(admin_id):
            await self.admins_data.delete_one({'_id': admin_id})
            return

    async def get_all_admins(self):
        users_docs = await self.admins_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in users_docs]
        return user_ids


    # BAN USER DATA
    async def ban_user_exist(self, user_id: int):
        found = await self.banned_user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_ban_user(self, user_id: int):
        if not await self.ban_user_exist(user_id):
            await self.banned_user_data.insert_one({'_id': user_id})
            return

    async def del_ban_user(self, user_id: int):
        if await self.ban_user_exist(user_id):
            await self.banned_user_data.delete_one({'_id': user_id})
            return

    async def get_ban_users(self):
        users_docs = await self.banned_user_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in users_docs]
        return user_ids



    # AUTO DELETE TIMER SETTINGS
    async def set_del_timer(self, value: int):        
        existing = await self.del_timer_data.find_one({})
        if existing:
            await self.del_timer_data.update_one({}, {'$set': {'value': value}})
        else:
            await self.del_timer_data.insert_one({'value': value})

    async def get_del_timer(self):
        data = await self.del_timer_data.find_one({})
        if data:
            return data.get('value', 600)
        return 0


    # CHANNEL MANAGEMENT
    async def channel_exist(self, channel_id: int):
        found = await self.fsub_data.find_one({'_id': channel_id})
        return bool(found)

    async def add_channel(self, channel_id: int):
        if not await self.channel_exist(channel_id):
            await self.fsub_data.insert_one({'_id': channel_id})
            return

    async def rem_channel(self, channel_id: int):
        if await self.channel_exist(channel_id):
            await self.fsub_data.delete_one({'_id': channel_id})
            return

    async def show_channels(self):
        channel_docs = await self.fsub_data.find().to_list(length=None)
        channel_ids = [doc['_id'] for doc in channel_docs]
        return channel_ids

    
    # CHANNEL MODE (REQUEST ON/OFF)
    async def set_channel_mode(self, channel_id: int, mode: str):
        await self.fsub_data.update_one(
            {'_id': channel_id},
            {'$set': {'mode': mode}},
            upsert=True
        )

    async def get_channel_mode(self, channel_id: int):
        data = await self.fsub_data.find_one({'_id': channel_id})
        return data.get('mode', 'off') if data else 'off'


    # REQUEST FORCE SUB CHANNEL TRACKING
    async def reqChannel_exist(self, channel_id: int):
        found = await self.rqst_fsub_Channel_data.find_one({'_id': channel_id})
        return bool(found)

    async def add_reqChannel(self, channel_id: int):
        if not await self.reqChannel_exist(channel_id):
            await self.rqst_fsub_Channel_data.insert_one({'_id': channel_id})
            return

    async def del_reqChannel(self, channel_id: int):
        if await self.reqChannel_exist(channel_id):
            await self.rqst_fsub_Channel_data.delete_one({'_id': channel_id})
            return

    async def get_req_channels(self):
        channel_docs = await self.rqst_fsub_Channel_data.find().to_list(length=None)
        channel_ids = [doc['_id'] for doc in channel_docs]
        return channel_ids


    # REQUEST FORCE SUB USER TRACKING
    async def req_user_exist(self, channel_id: int, user_id: int):
        found = await self.rqst_fsub_data.find_one({'_id': f"{channel_id}_{user_id}"})
        return bool(found)

    async def req_user(self, channel_id: int, user_id: int):
        if not await self.req_user_exist(channel_id, user_id):
            await self.rqst_fsub_data.insert_one({'_id': f"{channel_id}_{user_id}", 'channel_id': channel_id, 'user_id': user_id})
            return

    async def del_req_user(self, channel_id: int, user_id: int):
        if await self.req_user_exist(channel_id, user_id):
            await self.rqst_fsub_data.delete_one({'_id': f"{channel_id}_{user_id}"})
            return

    async def get_req_users(self, channel_id: int):
        user_docs = await self.rqst_fsub_data.find({'channel_id': channel_id}).to_list(length=None)
        user_ids = [doc['user_id'] for doc in user_docs]
        return user_ids


    # VERIFICATION TOKEN SYSTEM
    async def get_verify_status(self, user_id: int):
        user = await self.user_data.find_one({'_id': user_id})
        if user:
            return user.get('verify_status', default_verify)
        return default_verify

    async def update_verify_status(self, user_id: int, **kwargs):
        if not await self.present_user(user_id):
            await self.add_user(user_id)

        user = await self.user_data.find_one({'_id': user_id})
        current_verify = user.get('verify_status', default_verify) if user else default_verify

        for key, value in kwargs.items():
            current_verify[key] = value

        await self.user_data.update_one(
            {'_id': user_id},
            {'$set': {'verify_status': current_verify}},
            upsert=True
        )

    async def get_verify_count(self, user_id: int):
        user = await self.user_data.find_one({'_id': user_id})
        return user.get('verify_count', 0) if user else 0

    async def set_verify_count(self, user_id: int, count: int):
        await self.user_data.update_one(
            {'_id': user_id},
            {'$set': {'verify_count': count}},
            upsert=True
        )

    async def reset_all_verify_counts(self):
        await self.user_data.update_many({}, {'$set': {'verify_count': 0}})


    # SHORTENER ROTATION TRACKING
    async def get_user_shortener_history(self, user_id: int):
        """Get user's shortener usage history"""
        user = await self.user_data.find_one({'_id': user_id})
        if user and 'shortener_history' in user:
            return user['shortener_history']
        return []

    async def update_user_shortener_history(self, user_id: int, shortener_index: int):
        """Update user's shortener usage history"""
        if not await self.present_user(user_id):
            await self.add_user(user_id)
            
        await self.user_data.update_one(
            {'_id': user_id},
            {
                '$push': {
                    'shortener_history': {
                        'index': shortener_index,
                        'used_at': time.time()
                    }
                }
            },
            upsert=True
        )

    async def get_next_shortener_for_user(self, user_id: int, total_shorteners: int):
        """Get next shortener index for user based on rotation"""
        history = await self.get_user_shortener_history(user_id)
        
        if not history:
            return 0  # First shortener for new user
        
        # Get unique shortener indices used
        used_indices = set(item['index'] for item in history)
        
        # If user has used all shorteners, reset and start from 0
        if len(used_indices) >= total_shorteners:
            # Clear history and start fresh cycle
            await self.user_data.update_one(
                {'_id': user_id},
                {'$unset': {'shortener_history': ''}}
            )
            return 0
        
        # Find next unused shortener
        for i in range(total_shorteners):
            if i not in used_indices:
                return i
        
        return 0  # Fallback

    async def reset_user_shortener_cycle(self, user_id: int):
        """Reset user's shortener rotation cycle"""
        await self.user_data.update_one(
            {'_id': user_id},
            {'$unset': {'shortener_history': ''}}
        )

    async def get_shortener_usage_stats(self, limit: int = 1000):
        """Get shortener usage statistics"""
        try:
            pipeline = [
                {'$match': {'shortener_history': {'$exists': True, '$ne': []}}},
                {'$limit': limit},
                {'$unwind': '$shortener_history'},
                {'$group': {
                    '_id': '$shortener_history.index',
                    'count': {'$sum': 1},
                    'users': {'$addToSet': '$_id'}
                }},
                {'$sort': {'_id': 1}}
            ]
            
            cursor = self.user_data.aggregate(pipeline)
            stats = []
            async for doc in cursor:
                stats.append({
                    'shortener_index': doc['_id'],
                    'usage_count': doc['count'],
                    'unique_users': len(doc['users'])
                })
            
            return stats
        except Exception as e:
            logging.error(f"Error getting shortener stats: {e}")
            return []


db = Yae_X_Miko(DB_URI, DB_NAME)
