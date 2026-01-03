import telebot
from telebot import types
import re
import os
import time

# ==========================================
# 👇 Bot Token ထည့်ပါ
# ==========================================
BOT_TOKEN = '8023746280:AAHPKiTBsQ96nTwEfuetXuwuITLzHJTaJ38'

bot = telebot.TeleBot(BOT_TOKEN)

# User Data Storage
user_data = {}

# CC Regex Function
def extract_cards(text):
    regex = r'\d{15,16}[\|\:\/\-\s]\d{1,2}[\|\:\/\-\s]\d{2,4}[\|\:\/\-\s]\d{3,4}'
    cards = re.findall(regex, text)
    cleaned = set()
    for card in cards:
        clean_card = re.sub(r'[ \:\/\-]', '|', card)
        cleaned.add(clean_card)
    return list(cleaned)

# Helper: Load Persistent Old Cards
def load_old_cards(chat_id):
    filename = f"old_cards_{chat_id}.txt"
    if not os.path.exists(filename):
        return set()
    with open(filename, "r") as f:
        return set(line.strip() for line in f if line.strip())

# Helper: Save to Persistent Old Cards
def save_old_cards(chat_id, new_cards_list):
    filename = f"old_cards_{chat_id}.txt"
    with open(filename, "a") as f:
        for card in new_cards_list:
            f.write(card + "\n")

# Helper: Clear Persistent Old Cards
def clear_old_cards(chat_id):
    filename = f"old_cards_{chat_id}.txt"
    if os.path.exists(filename):
        os.remove(filename)
        return True
    return False

# Helper: Ensure User Data Exists
def ensure_user_data(chat_id):
    if chat_id not in user_data:
        user_data[chat_id] = {'mode': 'idle', 'files': [], 'new_session': set(), 'last_fresh': []}

# ==========================================
# 🏠 MAIN MENU
# ==========================================
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id)
    user_data[chat_id]['mode'] = 'idle'
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🧹 Cleaner & Combiner")
    btn2 = types.KeyboardButton("🔍 Smart Filter (Persistent)")
    btn3 = types.KeyboardButton("🗑️ Clear Old Database")
    markup.add(btn1, btn2, btn3)
    
    old_count = len(load_old_cards(chat_id))
    
    bot.reply_to(message, 
        f"🤖 **Super Tool Bot**\n"
        f"📊 **Saved Old Cards:** `{old_count}`\n\n"
        "လိုချင်တဲ့ လုပ်ဆောင်ချက်ကို ရွေးချယ်ပါ:\n\n"
        "🧹 **Cleaner & Combiner:**\n"
        "ဖိုင်တွေပေါင်းမယ်၊ သန့်မယ်။\n\n"
        "🔍 **Smart Filter (Persistent):**\n"
        "Database နဲ့တိုက်ပြီး အသစ်တွေကိုပဲ ယူမယ်။\n\n"
        "🗑️ **Clear Old Database:**\n"
        "Database ကို ရှင်းမယ် (Reset)।",
        reply_markup=markup
    )

# 🔥 COMMAND: Clear Old Database
@bot.message_handler(commands=['cleanold'])
def clean_old_command(message):
    chat_id = message.chat.id
    if clear_old_cards(chat_id):
        bot.reply_to(message, "✅ **Success!** Old cards database has been cleared.")
    else:
        bot.reply_to(message, "⚠️ Database is already empty.")

@bot.message_handler(func=lambda m: m.text == "🗑️ Clear Old Database")
def btn_clean_old(message):
    clean_old_command(message)

# ==========================================
# MODE 1: CLEANER
# ==========================================
@bot.message_handler(func=lambda m: m.text == "🧹 Cleaner & Combiner")
def mode_cleaner(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id)
    
    user_data[chat_id]['mode'] = 'cleaner'
    user_data[chat_id]['files'] = []
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_done = types.KeyboardButton("✅ Done Combining")
    btn_cancel = types.KeyboardButton("❌ Main Menu")
    markup.add(btn_done, btn_cancel)
    
    bot.reply_to(message, "🧹 **Cleaner Mode!**\nSend files now...", reply_markup=markup)

# ==========================================
# MODE 2: SMART FILTER
# ==========================================
@bot.message_handler(func=lambda m: m.text == "🔍 Smart Filter (Persistent)")
def mode_filter_start(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id)
    user_data[chat_id]['mode'] = 'filter_router'
    
    old_count = len(load_old_cards(chat_id))
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_add_old = types.KeyboardButton("📥 Add to Old Database")
    btn_check_new = types.KeyboardButton("⚡ Check New Files")
    btn_cancel = types.KeyboardButton("❌ Main Menu")
    markup.add(btn_add_old, btn_check_new, btn_cancel)
    
    bot.reply_to(message, 
        f"🔍 **Filter Mode** (Old Cards: `{old_count}`)\n\n"
        "1️⃣ **Add to Old:** Old File တွေကို Database ထဲထည့်မယ်။\n"
        "2️⃣ **Check New:** New File တွေကို စစ်မယ် (Old တွေကို ဖယ်မယ်)။",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "📥 Add to Old Database")
def submode_add_old(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id)
    user_data[chat_id]['mode'] = 'adding_old'
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_back = types.KeyboardButton("🔙 Back to Filter Menu")
    markup.add(btn_back)
    
    bot.reply_to(message, "📥 **Send Old Files NOW.**\nDatabase ထဲသိမ်းမယ့် ဖိုင်ကို ပို့ပေးပါ။", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "⚡ Check New Files")
def submode_check_new(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id)
    user_data[chat_id]['mode'] = 'checking_new'
    user_data[chat_id]['new_session'] = set()
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_finish = types.KeyboardButton("✅ Finish & Filter")
    btn_back = types.KeyboardButton("🔙 Back to Filter Menu")
    markup.add(btn_finish, btn_back)
    
    bot.reply_to(message, "⚡ **Send New Files NOW.**\nDuplicate တွေကို ဖယ်ထုတ်ပေးမယ်။", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔙 Back to Filter Menu")
def back_to_filter(message):
    mode_filter_start(message)

# ==========================================
# ⚙️ LOGIC HANDLERS
# ==========================================
@bot.message_handler(func=lambda m: m.text == "✅ Done Combining")
def process_cleaner(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id)
    if user_data[chat_id]['mode'] != 'cleaner': return

    all_cards = user_data[chat_id]['files']
    if not all_cards:
        bot.reply_to(message, "❌ No files sent.")
        return
        
    unique_cards = list(set(all_cards))
    removed = len(all_cards) - len(unique_cards)
    
    caption = f"🧹 **Cleaning Done!**\n💎 Unique: {len(unique_cards)}\n🗑️ Removed: {removed}"
    send_file_result(message, unique_cards, "Combined.txt", caption)
    send_welcome(message)

@bot.message_handler(func=lambda m: m.text == "✅ Finish & Filter")
def process_filter_final(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id)
    if user_data[chat_id]['mode'] != 'checking_new': return

    new_input = user_data[chat_id]['new_session']
    if not new_input:
        bot.reply_to(message, "❌ No new cards sent.")
        return

    bot.reply_to(message, "⏳ Checking Database...")
    old_db = load_old_cards(chat_id)
    
    final_fresh = list(new_input - old_db)
    removed_count = len(new_input) - len(final_fresh)
    
    # Store strictly fresh cards to let user save them later
    user_data[chat_id]['last_fresh'] = final_fresh

    if final_fresh:
        caption = (
            f"🔍 **Filter Result:**\n"
            f"📥 Input: {len(new_input)}\n"
            f"🗑️ Old/Dupes: {removed_count}\n"
            f"💎 **Fresh: {len(final_fresh)}**"
        )
        
        # Send File
        send_file_result(message, final_fresh, "Fresh_Filtered.txt", caption)
        
        # 🔥 AUTO ADD BUTTON 🔥
        markup = types.InlineKeyboardMarkup()
        btn_save = types.InlineKeyboardButton("💾 Save Fresh to Database", callback_data="save_fresh_to_db")
        markup.add(btn_save)
        
        bot.send_message(chat_id, "💡 ဒီ Fresh Cards တွေကို Old Database ထဲ ထပ်ဖြည့်မလား?\n(နောက်တစ်ခါစစ်ရင် ဒါတွေကိုပါ ဖယ်ပေးသွားမယ်)", reply_markup=markup)
        
    else:
        bot.reply_to(message, "❌ **No Fresh Cards!**\nAll cards are already in Database.")
        send_welcome(message)

@bot.callback_query_handler(func=lambda call: call.data == "save_fresh_to_db")
def callback_save_fresh(call):
    chat_id = call.message.chat.id
    ensure_user_data(chat_id)
    
    fresh_cards = user_data[chat_id].get('last_fresh', [])
    
    if fresh_cards:
        save_old_cards(chat_id, fresh_cards)
        user_data[chat_id]['last_fresh'] = [] # Clear after saving
        
        new_total = len(load_old_cards(chat_id))
        bot.edit_message_text(f"✅ **Saved!**\nNow Database has `{new_total}` cards.", chat_id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "Already saved or expired.")

# Helper to send file
def send_file_result(message, data_list, filename, caption):
    if not data_list: return
    with open(filename, "w") as f:
        for item in data_list: f.write(item + "\n")
    with open(filename, "rb") as f:
        bot.send_document(message.chat.id, f, caption=caption)
    os.remove(filename)

# General Handler
@bot.message_handler(content_types=['document', 'text'])
def handle_inputs(message):
    chat_id = message.chat.id
    if message.text == "❌ Main Menu":
        send_welcome(message)
        return
        
    ensure_user_data(chat_id)
    mode = user_data[chat_id]['mode']
    
    # Only process if in correct mode
    if mode not in ['cleaner', 'adding_old', 'checking_new']:
        if message.text and not message.text.startswith('/'):
             # ignore random text
             return

    # Extract Logic
    content = ""
    if message.content_type == 'text': content = message.text
    elif message.content_type == 'document':
        try:
            file_info = bot.get_file(message.document.file_id)
            content = bot.download_file(file_info.file_path).decode('utf-8', errors='ignore')
        except: return

    extracted = extract_cards(content)
    if not extracted: 
        if mode != 'idle': bot.reply_to(message, "⚠️ No cards found.")
        return

    # Route Data
    if mode == 'cleaner':
        user_data[chat_id]['files'].extend(extracted)
        bot.reply_to(message, f"📥 Added! (Total: {len(user_data[chat_id]['files'])})")
        
    elif mode == 'adding_old':
        save_old_cards(chat_id, extracted) # 🔥 Save Immediately
        total = len(load_old_cards(chat_id))
        bot.reply_to(message, f"💾 **Saved to Database!**\nTotal Old Cards: `{total}`")
        
    elif mode == 'checking_new':
        user_data[chat_id]['new_session'].update(extracted)
        bot.reply_to(message, f"📥 New Input: {len(user_data[chat_id]['new_session'])}")

print("🤖 Persistent Bot Running...")
while True:
    try:
        bot.polling(non_stop=True, timeout=60)
    except Exception as e:
        time.sleep(5)
