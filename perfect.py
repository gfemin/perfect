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

# User Session Data (Temporary state for current operation)
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
        # Read lines and strip whitespace
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
        user_data[chat_id] = {'mode': 'idle', 'files': [], 'new_session': set()}

# ==========================================
# 🏠 MAIN MENU & COMMANDS
# ==========================================
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id)
    user_data[chat_id]['mode'] = 'idle'
    user_data[chat_id]['files'] = []
    user_data[chat_id]['new_session'] = set()
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🧹 Cleaner & Combiner")
    btn2 = types.KeyboardButton("🔍 Smart Filter (Persistent)")
    btn3 = types.KeyboardButton("🗑️ Clear Old Database")
    markup.add(btn1, btn2, btn3)
    
    old_count = len(load_old_cards(chat_id))
    
    bot.reply_to(message, 
        f"🤖 **Super Tool Bot**\n"
        f"📊 Saved Old Cards: `{old_count}`\n\n"
        "လိုချင်တဲ့ လုပ်ဆောင်ချက်ကို ရွေးချယ်ပါ:\n\n"
        "🧹 **Cleaner & Combiner:**\n"
        "ဖိုင်တွေအများကြီး ပေါင်းမယ်၊ ရှုပ်နေတာတွေ သန့်မယ်။\n\n"
        "🔍 **Smart Filter (Persistent):**\n"
        "Save ထားတဲ့ Old Cards တွေနဲ့ တိုက်စစ်မယ်။\n"
        "(Old File ထပ်ပို့စရာမလို၊ New ပဲပို့ရုံမယ်)\n\n"
        "🗑️ **Clear Old Database:**\n"
        "သိမ်းထားတဲ့ Old Cards တွေကို ဖျက်မယ်။ (/cleanold)",
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
# MODE 1: CLEANER & COMBINER
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
    
    bot.reply_to(message, 
        "🧹 **Cleaner Mode Selected!**\n\n"
        "ဖိုင်တွေ (သို့) စာတွေကို တစ်ခုပြီးတစ်ခု ပို့ပေးပါ။\n"
        "အားလုံးပို့ပြီးရင် **Done** ကို နှိပ်ပါ။",
        reply_markup=markup
    )

# ==========================================
# MODE 2: SMART FILTER (PERSISTENT)
# ==========================================
@bot.message_handler(func=lambda m: m.text == "🔍 Smart Filter (Persistent)")
def mode_filter_start(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id)

    # ဒီ Mode မှာ Old File ထပ်ပို့စရာမလိုတော့ဘူး။
    # ရှိပြီးသား Database ကို သုံးမှာမို့လို့ တန်းပြီး New File တောင်းမယ်။ Or user can add to old.
    
    user_data[chat_id]['mode'] = 'filter_router' # Sub-menu for filter
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_add_old = types.KeyboardButton("📥 Add to Old Database")
    btn_check_new = types.KeyboardButton("⚡ Check New Files")
    btn_cancel = types.KeyboardButton("❌ Main Menu")
    markup.add(btn_add_old, btn_check_new, btn_cancel)
    
    old_count = len(load_old_cards(chat_id))
    
    bot.reply_to(message, 
        f"🔍 **Smart Filter Mode**\n"
        f"📂 Current Old Database: `{old_count}` cards\n\n"
        "1️⃣ **Add to Old Database:**\n"
        "နောက်ထပ် Old File တွေ ထပ်ဖြည့်ချင်ရင် ရွေးပါ။\n\n"
        "2️⃣ **Check New Files:**\n"
        "ဖိုင်အသစ်တွေ စစ်ချင်ရင် ရွေးပါ။ (Database ထဲကဟာတွေ ဖယ်ပေးမယ်)",
        reply_markup=markup
    )

# Sub-mode: Add to Old
@bot.message_handler(func=lambda m: m.text == "📥 Add to Old Database")
def submode_add_old(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id)
    user_data[chat_id]['mode'] = 'adding_old'
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_back = types.KeyboardButton("🔙 Back to Filter Menu")
    markup.add(btn_back)
    
    bot.reply_to(message, "📥 **Send Old Files/Text now.**\nI will save them to database.", reply_markup=markup)

# Sub-mode: Check New
@bot.message_handler(func=lambda m: m.text == "⚡ Check New Files")
def submode_check_new(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id)
    user_data[chat_id]['mode'] = 'checking_new'
    user_data[chat_id]['new_session'] = set() # Reset for this batch
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_finish = types.KeyboardButton("✅ Finish & Filter")
    btn_back = types.KeyboardButton("🔙 Back to Filter Menu")
    markup.add(btn_finish, btn_back)
    
    bot.reply_to(message, "⚡ **Send New Files/Text now.**\nI will remove duplicates from Old Database.", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔙 Back to Filter Menu")
def back_to_filter(message):
    mode_filter_start(message)

# ==========================================
# ⚙️ PROCESSING LOGIC
# ==========================================

# 1. Cleaner Processing
@bot.message_handler(func=lambda m: m.text == "✅ Done Combining")
def process_cleaner(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id)

    if user_data[chat_id]['mode'] != 'cleaner':
        bot.reply_to(message, "⚠️ Mode Error. Please restart.")
        return

    all_cards = user_data[chat_id]['files']
    if not all_cards:
        bot.reply_to(message, "❌ ဖိုင်မရှိသေးပါ။")
        return
        
    unique_cards = list(set(all_cards))
    removed = len(all_cards) - len(unique_cards)
    
    caption = f"🧹 **Cleaning Done!**\n💎 Unique: {len(unique_cards)}\n🗑️ Dupes Removed: {removed}"
    send_file_result(message, unique_cards, "Combined_Cleaned.txt", caption)
    send_welcome(message)

# 2. Filter Processing (Final Step)
@bot.message_handler(func=lambda m: m.text == "✅ Finish & Filter")
def process_filter_final(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id)

    if user_data[chat_id]['mode'] != 'checking_new':
        bot.reply_to(message, "⚠️ Mode Error. Please restart.")
        return

    new_input_cards = user_data[chat_id]['new_session']
    
    if not new_input_cards:
        bot.reply_to(message, "❌ No cards sent.")
        return

    bot.reply_to(message, "⏳ Comparing with Old Database...")
    
    # Load Old Database
    old_database = load_old_cards(chat_id)
    
    # Logic: New Input - Old Database
    final_fresh = new_input_cards - old_database
    removed_dupes = len(new_input_cards) - len(final_fresh)
    
    # Optional: Save these fresh cards to Old Database automatically? 
    # Usually, we don't, unless user treats them as 'checked'.
    # For now, we just give the fresh file.
    
    if final_fresh:
        caption = (
            f"🔍 **Filter Complete!**\n"
            f"📂 Old Database Size: {len(old_database)}\n"
            f"📥 Input Size: {len(new_input_cards)}\n"
            f"💎 **Fresh Cards: {len(final_fresh)}**\n"
            f"(Removed {removed_dupes} duplicates found in Old DB)"
        )
        send_file_result(message, list(final_fresh), "Fresh_Filtered.txt", caption)
        
        # Ask user if they want to add these fresh cards to Old DB
        # For simplicity, let's just go back to menu. 
        # User can upload "Fresh_Filtered.txt" to "Add Old" if they processed it.
    else:
        bot.reply_to(message, "❌ **No Fresh Cards!**\nAll uploaded cards are already in your Old Database.")
        
    send_welcome(message)

# Helper to send file
def send_file_result(message, data_list, filename, caption):
    if not data_list:
        return
        
    with open(filename, "w") as f:
        for item in data_list:
            f.write(item + "\n")
            
    with open(filename, "rb") as f:
        bot.send_document(message.chat.id, f, caption=caption)
    os.remove(filename)

# ==========================================
# 📂 GENERAL FILE HANDLER
# ==========================================
@bot.message_handler(content_types=['document', 'text'])
def handle_inputs(message):
    chat_id = message.chat.id
    
    if message.text == "❌ Main Menu":
        send_welcome(message)
        return
        
    ensure_user_data(chat_id)
    mode = user_data[chat_id]['mode']

    if mode == 'idle' or mode == 'filter_router':
        if message.text != "/start" and not message.text.startswith("/"):
             # Ignore random text in menus
             return

    # Get Content
    content = ""
    if message.content_type == 'text':
        content = message.text
    elif message.content_type == 'document':
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            content = downloaded.decode('utf-8', errors='ignore')
        except:
            bot.reply_to(message, "⚠️ File Error.")
            return

    extracted = extract_cards(content)
    if not extracted:
        # Only reply warning if user is in an input mode
        if mode in ['cleaner', 'adding_old', 'checking_new']:
            bot.reply_to(message, "⚠️ No CCs found.")
        return

    # Route Data
    if mode == 'cleaner':
        user_data[chat_id]['files'].extend(extracted)
        bot.reply_to(message, f"📥 Added to Cleaner! (Total: {len(user_data[chat_id]['files'])})")
        
    elif mode == 'adding_old':
        save_old_cards(chat_id, extracted) # Save immediately to file
        total_now = len(load_old_cards(chat_id))
        bot.reply_to(message, f"💾 Saved to Database! (Total Old: {total_now})")
        
    elif mode == 'checking_new':
        user_data[chat_id]['new_session'].update(extracted)
        bot.reply_to(message, f"📥 New Cards Received! (Total Input: {len(user_data[chat_id]['new_session'])})")

# ==========================================
# 🔥 SAFE POLLING
# ==========================================
print("🤖 Persistent Filter Bot is Running...")

while True:
    try:
        bot.polling(non_stop=True, timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"⚠️ Connection Error: {e}")
        time.sleep(5)
