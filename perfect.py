import telebot
from telebot import types
import re
import os

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

# Helper: Ensure User Data Exists (🔥 ဒီကောင်က Error ကာကွယ်ပေးမယ်)
def ensure_user_data(chat_id):
    if chat_id not in user_data:
        user_data[chat_id] = {'mode': 'idle', 'files': [], 'old': set(), 'new': set()}

# ==========================================
# 🏠 MAIN MENU
# ==========================================
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    chat_id = message.chat.id
    # Reset User State
    user_data[chat_id] = {'mode': 'idle', 'files': [], 'old': set(), 'new': set()}
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🧹 Cleaner & Combiner")
    btn2 = types.KeyboardButton("🔍 Smart Filter (Old vs New)")
    markup.add(btn1, btn2)
    
    bot.reply_to(message, 
        "🤖 **Super Tool Bot**\n\n"
        "လိုချင်တဲ့ လုပ်ဆောင်ချက်ကို ရွေးချယ်ပါ:\n\n"
        "🧹 **Cleaner & Combiner:**\n"
        "ဖိုင်တွေအများကြီး ပေါင်းမယ်၊ ရှုပ်နေတာတွေ သန့်မယ်။\n\n"
        "🔍 **Smart Filter (Old vs New):**\n"
        "Old Files (စစ်ပြီးသား) နဲ့ တိုက်ပြီး၊ New Files ထဲက အသစ်တွေကိုပဲ ယူမယ်။",
        reply_markup=markup
    )

# ==========================================
# MODE 1: CLEANER & COMBINER
# ==========================================
@bot.message_handler(func=lambda m: m.text == "🧹 Cleaner & Combiner")
def mode_cleaner(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id) # 🔥 Data မရှိရင် အသစ်ဆောက်မယ်
    
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
# MODE 2: SMART FILTER (OLD vs NEW)
# ==========================================
@bot.message_handler(func=lambda m: m.text == "🔍 Smart Filter (Old vs New)")
def mode_filter_start(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id) # 🔥 Data မရှိရင် အသစ်ဆောက်မယ် (KeyError မတက်တော့ဘူး)

    user_data[chat_id]['mode'] = 'filter_old' # Step 1
    user_data[chat_id]['old'] = set()
    user_data[chat_id]['new'] = set()
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_next = types.KeyboardButton("➡️ Next Step (Send New)")
    btn_cancel = types.KeyboardButton("❌ Main Menu")
    markup.add(btn_next, btn_cancel)
    
    bot.reply_to(message, 
        "🔍 **Smart Filter Selected!**\n\n"
        "1️⃣ **Step 1: Send OLD Files** (စစ်ပြီးသား)\n"
        "စစ်ပြီးသား ဖိုင်ဟောင်းတွေကို အရင်ပို့ပါ။\n"
        "ပြီးရင် **Next Step** နှိပ်ပါ။",
        reply_markup=markup
    )

# Filter Step 2 Transition
@bot.message_handler(func=lambda m: m.text == "➡️ Next Step (Send New)")
def mode_filter_step2(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id)
    
    if user_data[chat_id]['mode'] != 'filter_old':
        bot.reply_to(message, "⚠️ Please start from the beginning.")
        return
        
    user_data[chat_id]['mode'] = 'filter_new' # Step 2
    old_count = len(user_data[chat_id]['old'])
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_finish = types.KeyboardButton("✅ Finish & Filter")
    btn_cancel = types.KeyboardButton("❌ Main Menu")
    markup.add(btn_finish, btn_cancel)
    
    bot.reply_to(message, 
        f"✅ **Old Files Saved!** (Cards: {old_count})\n\n"
        "2️⃣ **Step 2: Send NEW Files** (မစစ်ရသေး)\n"
        "အခု မစစ်ရသေးတဲ့ ဖိုင်တွေကို ပို့ပါ။\n"
        "ပြီးရင် **Finish** နှိပ်ပါ။",
        reply_markup=markup
    )

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

# 2. Filter Processing
@bot.message_handler(func=lambda m: m.text == "✅ Finish & Filter")
def process_filter(message):
    chat_id = message.chat.id
    ensure_user_data(chat_id)

    if user_data[chat_id]['mode'] != 'filter_new':
        bot.reply_to(message, "⚠️ Mode Error. Please restart.")
        return

    old_set = user_data[chat_id]['old']
    new_set = user_data[chat_id]['new']
    
    bot.reply_to(message, "⏳ Calculating...")
    
    # Logic: New - Old
    final_fresh = new_set - old_set
    removed_dupes = len(new_set) - len(final_fresh)
    
    if final_fresh:
        caption = (
            f"🔍 **Filter Complete!**\n"
            f"📂 Old Database: {len(old_set)}\n"
            f"📥 New Inputs: {len(new_set)}\n"
            f"💎 **Fresh Cards: {len(final_fresh)}**\n"
            f"(Excluded {removed_dupes} old/duplicate cards)"
        )
        send_file_result(message, list(final_fresh), "Fresh_Filtered.txt", caption)
    else:
        bot.reply_to(message, "❌ **No Fresh Cards!**\nNew File ထဲက ကဒ်တွေအကုန်လုံး Old File ထဲမှာ ရှိပြီးသားပါ။")
        
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
        
    # 🔥 Data မရှိရင် အသစ်ဆောက်မယ် (Crash မဖြစ်အောင်)
    ensure_user_data(chat_id)

    if user_data[chat_id]['mode'] == 'idle':
        if message.text != "/start":
            send_welcome(message)
        return

    mode = user_data[chat_id]['mode']
    
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
        bot.reply_to(message, "⚠️ No CCs found.")
        return

    # Route Data to correct storage
    if mode == 'cleaner':
        user_data[chat_id]['files'].extend(extracted)
        bot.reply_to(message, f"📥 Added! (Total: {len(user_data[chat_id]['files'])})")
        
    elif mode == 'filter_old':
        user_data[chat_id]['old'].update(extracted)
        bot.reply_to(message, f"📥 Old Added! (Total Old: {len(user_data[chat_id]['old'])})")
        
    elif mode == 'filter_new':
        user_data[chat_id]['new'].update(extracted)
        bot.reply_to(message, f"📥 New Added! (Total New: {len(user_data[chat_id]['new'])})")

print("🤖 Super Bot is Running...")
bot.polling(non_stop=True)
