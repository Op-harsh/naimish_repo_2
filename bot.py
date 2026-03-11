import telebot
import time
import random
import string
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==========================================
# 🛑 DETAILS FILLED AUTOMATICALLY 🛑
# ==========================================
BOT_TOKEN = "8540132298:AAESYBJhh9o3fO1BGwGjz76-xSBh6dBNN18" 
BOT_USERNAME = "NS_LINK_SHARE_BOT" 
OWNER_ID = 5524906942 

# --- PRIVATE CHANNEL DETAILS ---
FORCE_SUB_CHANNEL_ID = -1002548609196 
FORCE_SUB_LINK = "https://t.me/+-FbPhX9Xm800NjA1" 

bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
#  DATABASE SETUP (SQLite)
# ==========================================
conn = sqlite3.connect('bot_database.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS channels (code TEXT PRIMARY KEY, channel_id TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
conn.commit()

cursor.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (OWNER_ID,))
conn.commit()

# ==========================================
# 🛠 HELPER FUNCTIONS
# ==========================================

def is_admin(user_id):
    cursor.execute("SELECT user_id FROM admins WHERE user_id=?", (user_id,))
    return cursor.fetchone() is not None

def check_force_sub(user_id):
    try:
        status = bot.get_chat_member(FORCE_SUB_CHANNEL_ID, user_id).status
        if status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        return False

def generate_unique_code(length=6):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

# ==========================================
#  MAIN COMMANDS (USERS)
# ==========================================

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    command_args = message.text.split(" ")
    
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    
    # --- FORCE SUB CHECK ---
    if not check_force_sub(user_id):
        markup = InlineKeyboardMarkup()
        join_btn = InlineKeyboardButton(" 𝗝𝗼𝗶𝗻 𝗢𝘂𝗿 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", url=FORCE_SUB_LINK)
        check_btn = InlineKeyboardButton(" 𝗜 𝗛𝗮𝘃𝗲 𝗝𝗼𝗶𝗻𝗲𝗱", callback_data="check_joined")
        markup.add(join_btn)
        markup.add(check_btn)
        
        bot.reply_to(message, "❌ <b>𝗣𝗹𝗲𝗮𝘀𝗲 𝗷𝗼𝗶𝗻 𝗼𝘂𝗿 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗳𝗶𝗿𝘀𝘁 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁!</b>", reply_markup=markup, parse_mode="HTML")
        return

    # --- DEEP LINK LOGIC (BUTTON UPDATE) ---
    if len(command_args) > 1:
        unique_code = command_args[1]
        
        cursor.execute("SELECT channel_id FROM channels WHERE code=?", (unique_code,))
        result = cursor.fetchone()
        
        if result:
            target_channel_id = result[0]
            try:
                expire_time = int(time.time()) + 120 
                invite_link = bot.create_chat_invite_link(
                    chat_id=target_channel_id,
                    expire_date=expire_time,
                    member_limit=1
                )
                
                # --- STYLISH BUTTON & TEXT ---
                text = "✅ <b>𝗛𝗲𝗿𝗲 𝗶𝘀 𝘆𝗼𝘂𝗿 𝗽𝗿𝗶𝘃𝗮𝘁𝗲 𝗹𝗶𝗻𝗸!</b>\n\n⏳ <i>This link will expire in exactly 2 minutes!</i>"
                link_markup = InlineKeyboardMarkup()
                link_btn = InlineKeyboardButton(" 𝗖𝗹𝗶𝗰𝗸 𝗧𝗼 𝗝𝗼𝗶𝗻 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", url=invite_link.invite_link)
                link_markup.add(link_btn)
                
                bot.reply_to(message, text, reply_markup=link_markup, parse_mode="HTML")
                
            except Exception as e:
                bot.reply_to(message, "❌ <b>𝗘𝗿𝗿𝗼𝗿:</b> Bot is not an Admin in the target channel.", parse_mode="HTML")
        else:
            bot.reply_to(message, "❌ <b>𝗧𝗵𝗶𝘀 𝗹𝗶𝗻𝗸 𝗶𝘀 𝗶𝗻𝘃𝗮𝗹𝗶𝗱 𝗼𝗿 𝗵𝗮𝘀 𝗲𝘅𝗽𝗶𝗿𝗲𝗱.</b>", parse_mode="HTML")
        return

    # --- WELCOME MESSAGE ---
    user_name = message.from_user.first_name.upper()
    text = f"» HEY!!, <b>{user_name} W/S</b>\n\n"
    text += "<code>LOVE TO WATCH ANIME SERIES AND MOVIES? I AM MADE TO HELP YOU TO FIND WHAT YOU'RE LOOKING FOR.</code>"

    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("• ABOUT •", callback_data="about_info"), InlineKeyboardButton("• CHANNELS •", callback_data="channels_list"))
    markup.add(InlineKeyboardButton("• Close •", callback_data="close_welcome"))

    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")

# ==========================================
#  ADMIN & OWNER COMMANDS
# ==========================================

@bot.message_handler(commands=['addch'])
def add_channel(message):
    if not is_admin(message.from_user.id): return
        
    try:
        channel_id = message.text.split(" ")[1]
        unique_code = f"ch_{generate_unique_code()}"
        
        cursor.execute("INSERT INTO channels (code, channel_id) VALUES (?, ?)", (unique_code, channel_id))
        conn.commit()
        
        permanent_link = f"https://t.me/{BOT_USERNAME}?start={unique_code}"
        text = f"✅ <b>𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗔𝗱𝗱𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆!</b>\n\n <b>𝗣𝗲𝗿𝗺𝗮𝗻𝗲𝗻𝘁 𝗕𝗼𝘁 𝗟𝗶𝗻𝗸:</b>\n{permanent_link}\n\n<i>Share this link. Users clicking it will get a 2-minute auto-revoke link.</i>"
        bot.reply_to(message, text, parse_mode="HTML")
    except IndexError:
        bot.reply_to(message, "⚠️ <b>𝗙𝗼𝗿𝗺𝗮𝘁:</b> <code>/addch -1001234567890</code>", parse_mode="HTML")

@bot.message_handler(commands=['delch'])
def del_channel(message):
    if not is_admin(message.from_user.id): return
    try:
        target = message.text.split(" ")[1]
        # Ab Channel ID ya Code dono se delete ho jayega
        cursor.execute("DELETE FROM channels WHERE code=? OR channel_id=?", (target, target))
        if cursor.rowcount > 0:
            conn.commit()
            bot.reply_to(message, f"✅ <b>𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗥𝗲𝗺𝗼𝘃𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆!</b>\n\n Target: <code>{target}</code>", parse_mode="HTML")
        else:
            bot.reply_to(message, "❌ <b>𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗡𝗼𝘁 𝗙𝗼𝘂𝗻𝗱!</b>\nCheck the ID or Code.", parse_mode="HTML")
    except IndexError:
        bot.reply_to(message, "⚠️ <b>𝗙𝗼𝗿𝗺𝗮𝘁:</b> <code>/delch <channel_id or code></code>", parse_mode="HTML")

@bot.message_handler(commands=['links'])
def show_links(message):
    if not is_admin(message.from_user.id): return
    cursor.execute("SELECT code, channel_id FROM channels")
    channels = cursor.fetchall()
    
    if not channels:
        return bot.reply_to(message, " <b>𝗡𝗼 𝗰𝗵𝗮𝗻𝗻𝗲𝗹𝘀 𝗮𝗱𝗱𝗲𝗱 𝘆𝗲𝘁.</b>", parse_mode="HTML")
        
    text = " <b>𝗔𝗹𝗹 𝗔𝗱𝗱𝗲𝗱 𝗖𝗵𝗮𝗻𝗻𝗲𝗹𝘀:</b>\n\n"
    for code, ch_id in channels:
        text += f"𝗜𝗗: <code>{ch_id}</code>\n https://t.me/{BOT_USERNAME}?start={code}\n\n"
    bot.reply_to(message, text, parse_mode="HTML")

# ==========================================
#  BUTTON CLICKS (CALLBACKS)
# ==========================================

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data == "check_joined":
        if check_force_sub(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ Thank you for joining!")
            bot.delete_message(chat_id, message_id)
            bot.send_message(chat_id, "✅ <b>𝗪𝗲𝗹𝗰𝗼𝗺𝗲!</b> You can now use the bot.\nSend /start again to continue.", parse_mode="HTML")
        else:
            bot.answer_callback_query(call.id, "❌ You haven't joined the channel yet!", show_alert=True)
    elif call.data == "close_welcome":
        try: bot.delete_message(chat_id, message_id)
        except: bot.answer_callback_query(call.id, "Error closing message.")
    elif call.data == "about_info":
        bot.answer_callback_query(call.id, "I am an Anime Link Provider Bot! 🤖 developer : @the_developer_harsh", show_alert=True)
    elif call.data == "channels_list":
        bot.answer_callback_query(call.id, "Join our main channels!", show_alert=True)

print("Stylish Bot is running! ")
bot.infinity_polling()

