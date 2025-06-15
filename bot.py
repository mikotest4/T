from aiohttp import web
from plugins import web_server
import asyncio
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
from config import *


name ="""
 BY Yae Miko
"""


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id = db_channel.id, text = "Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"ᴍᴀᴋᴇ sᴜʀᴇ ʙᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ ᴅʙ ᴄʜᴀɴɴᴇʟ, ᴀɴᴅ ᴅᴏᴜʙʟᴇ ᴄʜᴇᴄᴋ ᴛʜᴇ CHANNEL_ID ᴠᴀʟᴜᴇ, ᴄᴜʀʀᴇɴᴛ ᴠᴀʟᴜᴇ
{CHANNEL_ID}")
            self.LOGGER(__name__).info("\nʙᴏᴛ sᴛᴏᴘᴘᴇᴅ.")
            sys.exit()

        # Start Web Server
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()


        try: await self.send_message(OWNER_ID, text = f"<b>𝙼𝚊𝚜𝚝𝚎𝚛 𝚈𝚘𝚞𝚛 𝙱𝚘𝚝 𝙷𝚊𝚜 𝙱𝚎𝚎𝚗 𝚂𝚝𝚊𝚛𝚝𝚎𝚍!</b>")
        except: pass

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("ʙᴏᴛ sᴛᴏᴘᴘᴇᴅ.")

    def run(self):
        """Run the bot."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start())
        self.LOGGER(__name__).info("ʙᴏᴛ ɪs ʀᴜɴɴɪɴɢ ɴᴏᴡ. ᴍᴀᴅᴇ ʙʏ ʏᴀᴇ ᴍɪᴋᴏ")
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            self.LOGGER(__name__).info("sʜᴜᴛᴛɪɴɢ ᴅᴏᴡɴ...")
        finally:
            loop.run_until_complete(self.stop())
