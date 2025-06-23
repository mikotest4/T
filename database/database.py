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
            'verified_time': 0,
            'verify_token': "",
            'link': "",
            'shortener_data': {
                'next_shortener': 0,
                'used_shorteners': [],
                'cycle_complete': False,
                'last_updated': time.time()
            }
        }
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
        if data and 'mode' in data:
            return data['mode']
        return "off"  # Default mode


    # REQUEST FORCESUB MANAGEMENT
    async def reqChannel_exist(self, channel_id: int):
        found = await self.rqst_fsub_Channel_data.find_one({'_id': channel_id})
        return bool(found)

    async def req_Channel(self, channel_id: int):
        if not await self.reqChannel_exist(channel_id):
            await self.rqst_fsub_Channel_data.insert_one({'_id': channel_id})
            return

    async def del_req_Channel(self, channel_id: int):
        if await self.reqChannel_exist(channel_id):
            await self.rqst_fsub_Channel_data.delete_one({'_id': channel_id})
            return

    async def req_user_exist(self, channel_id: int, user_id: int):
        found = await self.rqst_fsub_data.find_one({'channel_id': channel_id, 'user_id': user_id})
        return bool(found)

    async def req_user(self, channel_id: int, user_id: int):
        if not await self.req_user_exist(channel_id, user_id):
            await self.rqst_fsub_data.insert_one({'channel_id': channel_id, 'user_id': user_id})
            return

    async def del_req_user(self, channel_id: int, user_id: int):
        if await self.req_user_exist(channel_id, user_id):
            await self.rqst_fsub_data.delete_one({'channel_id': channel_id, 'user_id': user_id})
            return


    # VERIFICATION SYSTEM
    async def update_verify_status(self, user_id: int, is_verified: bool = None, verified_time: float = None, verify_token: str = None, link: str = None, shortener_data: dict = None):
        """Update user verification status with all parameters"""
        try:
            if not await self.present_user(user_id):
                await self.add_user(user_id)
            
            update_data = {}
            
            if is_verified is not None:
                update_data['verify_status.is_verified'] = is_verified
            if verified_time is not None:
                update_data['verify_status.verified_time'] = verified_time  
            if verify_token is not None:
                update_data['verify_status.verify_token'] = verify_token
            if link is not None:
                update_data['verify_status.link'] = link
            if shortener_data is not None:
                update_data['verify_status.shortener_data'] = shortener_data
                
            if update_data:
                await self.user_data.update_one(
                    {'_id': user_id}, 
                    {'$set': update_data}
                )
            
        except Exception as e:
            logging.error(f"Error updating verify status for {user_id}: {e}")

    async def get_verify_status(self, user_id: int):
        """Get user verification status"""
        try:
            if not await self.present_user(user_id):
                await self.add_user(user_id)
                
            user = await self.user_data.find_one({'_id': user_id})
            if user and 'verify_status' in user:
                return user['verify_status']
            else:
                return {
                    'is_verified': False,
                    'verified_time': 0,
                    'verify_token': "",
                    'link': "",
                    'shortener_data': {
                        'next_shortener': 0,
                        'used_shorteners': [],
                        'cycle_complete': False,
                        'last_updated': time.time()
                    }
                }
        except Exception as e:
            logging.error(f"Error getting verify status for {user_id}: {e}")
            return {
                'is_verified': False,
                'verified_time': 0,
                'verify_token': "",
                'link': "",
                'shortener_data': {
                    'next_shortener': 0,
                    'used_shorteners': [],
                    'cycle_complete': False,
                    'last_updated': time.time()
                }
            }

    # VERIFY COUNT SYSTEM
    async def get_verify_count(self, user_id: int):
        """Get user's verification count"""
        try:
            user = await self.user_data.find_one({'_id': user_id})
            if user and 'verify_count' in user:
                return user['verify_count']
            return 0
        except Exception as e:
            logging.error(f"Error getting verify count for {user_id}: {e}")
            return 0

    async def set_verify_count(self, user_id: int, count: int):
        """Set user's verification count"""
        try:
            if not await self.present_user(user_id):
                await self.add_user(user_id)
            
            await self.user_data.update_one(
                {'_id': user_id},
                {'$set': {'verify_count': count}}
            )
        except Exception as e:
            logging.error(f"Error setting verify count for {user_id}: {e}")

    async def reset_all_verify_counts(self):
        """Reset all users' verify counts (daily reset)"""
        try:
            await self.user_data.update_many(
                {},
                {'$set': {'verify_count': 0}}
            )
            logging.info("All verify counts reset successfully")
        except Exception as e:
            logging.error(f"Error resetting verify counts: {e}")

    # SHORTENER DATA MANAGEMENT
    async def get_user_shortener_data(self, user_id: int):
        """Get user's shortener rotation data"""
        try:
            verify_status = await self.get_verify_status(user_id)
            return verify_status.get('shortener_data', {
                'next_shortener': 0,
                'used_shorteners': [],
                'cycle_complete': False,
                'last_updated': time.time()
            })
        except Exception as e:
            logging.error(f"Error getting shortener data for {user_id}: {e}")
            return {
                'next_shortener': 0,
                'used_shorteners': [],
                'cycle_complete': False,
                'last_updated': time.time()
            }

    async def update_user_shortener_data(self, user_id: int, shortener_data: dict):
        """Update user's shortener rotation data"""
        try:
            await self.update_verify_status(user_id, shortener_data=shortener_data)
        except Exception as e:
            logging.error(f"Error updating shortener data for {user_id}: {e}")

    # STATISTICS AND ANALYTICS
    async def get_total_users(self):
        """Get total number of users"""
        try:
            return await self.user_data.count_documents({})
        except Exception as e:
            logging.error(f"Error getting total users: {e}")
            return 0

    async def get_verified_users_count(self):
        """Get count of currently verified users"""
        try:
            return await self.user_data.count_documents({
                'verify_status.is_verified': True
            })
        except Exception as e:
            logging.error(f"Error getting verified users count: {e}")
            return 0

    async def get_users_by_shortener(self, shortener_index: int):
        """Get users currently using a specific shortener"""
        try:
            return await self.user_data.count_documents({
                'verify_status.shortener_data.next_shortener': shortener_index
            })
        except Exception as e:
            logging.error(f"Error getting users by shortener: {e}")
            return 0

    # CLEANUP FUNCTIONS
    async def cleanup_expired_verifications(self, expire_time: int):
        """Clean up expired verifications"""
        try:
            current_time = time.time()
            cutoff_time = current_time - expire_time
            
            result = await self.user_data.update_many(
                {
                    'verify_status.is_verified': True,
                    'verify_status.verified_time': {'$lt': cutoff_time}
                },
                {
                    '$set': {
                        'verify_status.is_verified': False,
                        'verify_status.verify_token': "",
                        'verify_status.link': "",
                        'verify_status.shortener_data.next_shortener': 0,
                        'verify_status.shortener_data.used_shorteners': [],
                        'verify_status.shortener_data.cycle_complete': False
                    }
                }
            )
            
            if result.modified_count > 0:
                logging.info(f"Cleaned up {result.modified_count} expired verifications")
            
            return result.modified_count
        except Exception as e:
            logging.error(f"Error cleaning up expired verifications: {e}")
            return 0

    async def reset_user_shortener_cycle(self, user_id: int):
        """Reset user's shortener cycle - for admin use"""
        try:
            shortener_data = {
                'next_shortener': 0,
                'used_shorteners': [],
                'cycle_complete': False,
                'last_updated': time.time()
            }
            
            await self.update_verify_status(user_id, shortener_data=shortener_data)
            return True
        except Exception as e:
            logging.error(f"Error resetting shortener cycle for user {user_id}: {e}")
            return False

    # BULK OPERATIONS
    async def get_users_with_incomplete_cycles(self):
        """Get users who haven't completed their shortener cycle"""
        try:
            users = await self.user_data.find({
                'verify_status.shortener_data.cycle_complete': False,
                'verify_status.shortener_data.used_shorteners': {'$ne': []}
            }).to_list(length=None)
            
            return [user['_id'] for user in users]
        except Exception as e:
            logging.error(f"Error getting users with incomplete cycles: {e}")
            return []

    async def reset_all_shortener_cycles(self):
        """Reset all users' shortener cycles - for admin use"""
        try:
            result = await self.user_data.update_many(
                {},
                {
                    '$set': {
                        'verify_status.shortener_data.next_shortener': 0,
                        'verify_status.shortener_data.used_shorteners': [],
                        'verify_status.shortener_data.cycle_complete': False,
                        'verify_status.shortener_data.last_updated': time.time()
                    }
                }
            )
            
            logging.info(f"Reset shortener cycles for {result.modified_count} users")
            return result.modified_count
        except Exception as e:
            logging.error(f"Error resetting all shortener cycles: {e}")
            return 0

# Create database instance
db = Yae_X_Miko(DB_URI, DB_NAME)
