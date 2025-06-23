import os
from os import environ,getenv
import logging
from logging.handlers import RotatingFileHandler

#--------------------------------------------
#Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "7540338860:AAExDJs6mQTZaLjNk4l1uwHuXVQD2t4DUTQ")
APP_ID = int(os.environ.get("APP_ID", "28614709")) #Your API ID from my.telegram.org
API_HASH = os.environ.get("API_HASH", "f36fd2ee6e3d3a17c4d244ff6dc1bac8") #Your API Hash from my.telegram.org
#--------------------------------------------

CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002583602391")) #Your db channel Id
OWNER = os.environ.get("OWNER", "Yae_X_Miko") # Owner username without @
OWNER_ID = int(os.environ.get("OWNER_ID", "7970350353")) # Owner id
#--------------------------------------------
PORT = os.environ.get("PORT", "9800")
#--------------------------------------------
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://Sanskari:aloksingh@cluster0.cclpr.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = os.environ.get("DATABASE_NAME", "Miko")
#--------------------------------------------
BAN_SUPPORT = os.environ.get("BAN_SUPPORT", None)
TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "200"))
#--------------------------------------------
START_PIC = os.environ.get("START_PIC", "https://telegra.ph/file/e159ff1c9c3e076669a91-fdb27e80269b152e44.jpg")
FORCE_PIC = os.environ.get("FORCE_PIC", "https://telegra.ph/file/e159ff1c9c3e076669a91-fdb27e80269b152e44.jpg")

#--------------------------------------------
# MULTIPLE SHORTENER ROTATION SYSTEM
SHORTLINK_URLS = [
    os.environ.get("SHORTLINK_URL_1", "seturl.in"),
    os.environ.get("SHORTLINK_URL_2", "gplinks.com"),
    os.environ.get("SHORTLINK_URL_3", "linkshortify.com")
]

SHORTLINK_APIS = [
    os.environ.get("SHORTLINK_API_1", "9e6437ea764b1cfe3f64a9b0c1637163b3e132ea"),
    os.environ.get("SHORTLINK_API_2", "199b972404fbffd931a1dd1ea98a84fbae043307"),
    os.environ.get("SHORTLINK_API_3", "65a44ff0a6ee84bf4c118bf26009a21dca68b6d1")
]

# Legacy support for single shortener (will be ignored if multiple shorteners are configured)
SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "reel2earn.com")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "74508ee9f003899307cca7addf6013053e1f567e")

# Verify expire time per shortener (6 hours = 21600 seconds)
VERIFY_EXPIRE = int(os.environ.get('VERIFY_EXPIRE', "60")) # 6 hours per shortener
TUT_VID = os.environ.get("TUT_VID","https://t.me/hwdownload/3")

#--------------------------------------------

#--------------------------------------------
HELP_TXT = "<b>ɪ ᴀᴍ ᴊᴜsᴛ ғɪʟᴇ sʜᴀʀɪɴɢ ʙᴏᴛ. ɴᴏᴛʜɪɴɢ ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ɢᴏ ʙᴀᴄᴋ.\nɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴘᴀɪᴅ ʙᴏᴛ ʜᴏsᴛɪɴɢ ʏᴏᴜ ᴄᴀɴ ᴅᴍ ᴍᴇ ʜᴇʀᴇ @Yae_X_Miko</b>"
ABOUT_TXT = "<b>◈ ᴄʀᴇᴀᴛᴏʀ: <a href=https://t.me/Yae_X_Miko>『𝚈𝚊𝚎 𝙼𝚒𝚔𝚘』❋𝄗⃝🦋 ⌞𝚆𝚊𝚛𝚕𝚘𝚛𝚍𝚜⌝ ㊋</a></b>"
#--------------------------------------------
#--------------------------------------------
START_MSG = os.environ.get("START_MESSAGE", "<b>ʜᴇʟʟᴏ {first}\n\nɪ ᴀᴍ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ, ɪ ᴄᴀɴ sᴛᴏʀᴇ ᴘʀɪᴠᴀᴛᴇ ғɪʟᴇs ɪɴ sᴘᴇᴄɪғɪᴇᴅ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴏᴛʜᴇʀ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss ɪᴛ ғʀᴏᴍ sᴘᴇᴄɪᴀʟ ʟɪɴᴋ.</b>")
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "ʜᴇʟʟᴏ {first}\n\n<b>ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ʀᴇʟᴏᴀᴅ button ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛᴇᴅ ꜰɪʟᴇ.</b>")

CMD_TXT = """<blockquote><b>» ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs:</b></blockquote>

<b>›› /dlt_time :</b> sᴇᴛ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ
<b>›› /check_dlt_time :</b> ᴄʜᴇᴄᴋ ᴄᴜʀʀᴇɴᴛ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ
<b>›› /dbroadcast :</b> ʙʀᴏᴀᴅᴄᴀsᴛ ᴅᴏᴄᴜᴍᴇɴᴛ / ᴠɪᴅᴇᴏ
<b>›› /ban :</b> ʙᴀɴ ᴀ ᴜꜱᴇʀ
<b>›› /unban :</b> ᴜɴʙᴀɴ ᴀ ᴜꜱᴇʀ
<b>›› /banlist :</b> ɢᴇᴛ ʟɪsᴛ ᴏꜰ ʙᴀɴɴᴇᴅ ᴜꜱᴇʀs
<b>›› /addchnl :</b> ᴀᴅᴅ ꜰᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ
<b>›› /delchnl :</b> ʀᴇᴍᴏᴠᴇ ꜰᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ
<b>›› /listchnl :</b> ᴠɪᴇᴡ ᴀᴅᴅᴇᴅ ᴄʜᴀɴɴᴇʟs
<b>›› /fsub_mode :</b> ᴛᴏɢɢʟᴇ ꜰᴏʀᴄᴇ sᴜʙ ᴍᴏᴅᴇ
<b>›› /pbroadcast :</b> sᴇɴᴅ ᴘʜᴏᴛᴏ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀs
<b>›› /add_admin :</b> ᴀᴅᴅ ᴀɴ ᴀᴅᴍɪɴ
<b>›› /deladmin :</b> ʀᴇᴍᴏᴠᴇ ᴀɴ ᴀᴅᴍɪɴ
<b>›› /admins :</b> ɢᴇᴛ ʟɪsᴛ ᴏꜰ ᴀᴅᴍɪɴs
<b>›› /addpremium :</b> ᴀᴅᴅ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ
<b>›› /premium_users :</b> ʟɪsᴛ ᴀʟʟ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀs
<b>›› /remove_premium :</b> ʀᴇᴍᴏᴠᴇ ᴘʀᴇᴍɪᴜᴍ ꜰʀᴏᴍ ᴀ ᴜꜱᴇʀ
<b>›› /myplan :</b> ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs
<b>›› /count :</b> ᴄᴏᴜɴᴛ verifications
<b>›› /rotation_stats :</b> ᴠɪᴇᴡ sʜᴏʀᴛᴇɴᴇʀ ʀᴏᴛᴀᴛɪᴏɴ sᴛᴀᴛs
<b>›› /reset_rotation :</b> ʀᴇsᴇᴛ ᴜsᴇʀ's ʀᴏᴛᴀᴛɪᴏɴ ᴄʏᴄʟᴇ
"""
#--------------------------------------------
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", None) #set your Custom Caption here, Keep None for Disable Custom Caption
PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "True") == "True" else False #set True if you want to prevent users from forwarding files from bot
#--------------------------------------------
#Set true if you want Disable your Channel Posts Share button
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'True'
#--------------------------------------------
BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "ʙᴀᴋᴋᴀ ! ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴍʏ ꜱᴇɴᴘᴀɪ!!"

#==========================(BUY PREMIUM)====================#

OWNER_TAG = os.environ.get("OWNER_TAG", "@Yae_X_Miko")
UPI_ID = os.environ.get("UPI_ID", "ᴀsᴋ ғʀᴏᴍ ᴏᴡɴᴇʀ")
SCREENSHOT_URL = os.environ.get("SCREENSHOT_URL", "https://t.me/yae_x_miko")
QR_PIC = os.environ.get("QR_PIC", "https://telegra.ph/file/e159ff1c9c3e076669a91-fdb27e80269b152e44.jpg")

PRICE1 = os.environ.get("PRICE1", "15 ʀᴜᴘᴇᴇs")
PRICE2 = os.environ.get("PRICE2", "50 ʀᴜᴘᴇᴇs")
PRICE3 = os.environ.get("PRICE3", "100 ʀᴜᴘᴇᴇs")
PRICE4 = os.environ.get("PRICE4", "200 ʀᴜᴘᴇᴇs")
PRICE5 = os.environ.get("PRICE5", "300 ʀᴜᴘᴇᴇs")

#==========================================================#

ADMINS.append(OWNER_ID)
ADMINS.append(8108281129)

#---------------------------------------------------------------
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
