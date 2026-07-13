import telebot
import requests
from datetime import datetime
from io import BytesIO
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= CONFIG =================
BOT_TOKEN = "8912601476:AAGeeTnJx498Xd5MP1hVrYpFkEszIG84BIM"  # ⚠️ Token shared in plain text
bot = telebot.TeleBot(BOT_TOKEN)

# 📢 FORCE JOIN CHANNELS CONFIG (এখানে আপনার চ্যানেল/গ্রুপের আইডি বা ইউজারনেম দিন)
CHANNEL_1_ID = "@TestAdminBotS"   # উদাহরণ: "@my_main_channel" অথবা ID -100xxxxxxxxx
CHANNEL_2_ID = "@asdasdsa11c"   # উদাহরণ: "@my_sub_channel" অথবা ID -100xxxxxxxxx

CHANNEL_1_LINK = "https://t.me/TestAdminBotS"  # বাটন ১ এর লিঙ্ক
CHANNEL_2_LINK = "https://t.me/asdasdsa11c"  # বাটন ২ এর লিঙ্ক

# ========= API LINKS =========
INFO_API = "https://nirob-x-info.vercel.app/info?uid={uid}"
WELCOME_IMAGE = "https://freeimage.host/i/C07A0Cu"

TELEGRAM_MAX_LEN = 4096

# ========= LOGGING =========
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# ========= CHECK JOIN FUNCTION =========
def is_user_joined(user_id):
    """ইউজার দুটি চ্যানেলে জয়েন আছে কিনা চেক করার ফাংশন"""
    try:
        # চ্যানেল ১ চেক
        member1 = bot.get_chat_member(CHANNEL_1_ID, user_id)
        # চ্যানেল ২ চেক
        member2 = bot.get_chat_member(CHANNEL_2_ID, user_id)

        # লেফট, কিকড বা রেস্ট্রিক্টেড না হলে সে মেম্বার
        valid_statuses = ['member', 'administrator', 'creator']
        if member1.status in valid_statuses and member2.status in valid_statuses:
            return True
        return False
    except Exception as e:
        logging.error(f"Error checking channel membership: {e}")
        # বট অ্যাডমিন না থাকলে বা কোনো সমস্যা হলে সেফ সাইড হিসেবে True রিটার্ন করতে পারেন,
        # তবে সঠিকভাবে সেটআপ করলে এটি ঠিকঠাক কাজ করবে।
        return False


# ========= FORCE JOIN KEYBOARD =========
def get_join_keyboard(uid, command_type="info"):
    """ইউজার জয়েন না থাকলে ২টা চ্যানেল এবং ১টা ভেরিফাই বাটন শো করার কিবোর্ড"""
    markup = InlineKeyboardMarkup(row_width=2)

    # প্রথম লাইনে ২টি চ্যানেলের বাটন পাশাপাশি (আপনার দেওয়া ছবির মতো)
    btn1 = InlineKeyboardButton("📢 JOIN GROUP 1", url=CHANNEL_1_LINK)
    btn2 = InlineKeyboardButton("📢 JOIN GROUP 2", url=CHANNEL_2_LINK)
    markup.row(btn1, btn2)

    # দ্বিতীয় লাইনে বড় ভেরিফাই বাটন (Callback Data সহ যাতে পরে চেক করা যায়)
    # ডাটা ফরম্যাট: verify_কমান্ড_ইউআইডি
    verify_btn = InlineKeyboardButton("✅ VERIFY", callback_data=f"verify_{command_type}_{uid}")
    markup.row(verify_btn)

    return markup


# ========= SAFE GET HELPER =========
def safe_str(value, default="N/A"):
    if value is None or value == "":
        return default
    return str(value)


def safe_replace(value, prefix, default="N/A"):
    if value is None:
        return default
    return str(value).replace(prefix, "")


# ========= CONVERT TIME =========
def convert_time(timestamp):
    try:
        if not timestamp:
            return "Not Found"
        ts = int(str(timestamp).strip())
        if ts > 1000000000000:
            ts = ts / 1000
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "Not Found"


# ========= FORMAT INFO =========
def format_player_info(data, uid):
    basic = data.get("basicInfo") or {}
    profile = data.get("profileInfo") or {}
    clan = data.get("clanBasicInfo") or {}
    captain = data.get("captainBasicInfo") or {}
    pet = data.get("petInfo") or {}
    social = data.get("socialInfo") or {}
    credit = data.get("creditScoreInfo") or {}
    diamond = data.get("diamondCostRes") or {}

    skills = profile.get("equipedSkills") or []
    weapons = basic.get("weaponSkinShows") or []
    clothes = profile.get("clothes") or []

    rank_names = {0: 'Bronze', 1: 'Silver', 2: 'Gold', 3: 'Platinum', 4: 'Diamond',
                  5: 'Heroic', 6: 'Grandmaster', 301: 'Master'}
    br_rank = rank_names.get(basic.get("rank"), safe_str(basic.get("rank")))
    cs_rank = rank_names.get(basic.get("csRank"), safe_str(basic.get("csRank")))

    account_age = "N/A"
    create_at = basic.get("createAt")
    if create_at:
        try:
            created = datetime.fromtimestamp(int(create_at))
            days = (datetime.now() - created).days
            if days < 30:
                account_age = f"{days} days"
            elif days < 365:
                account_age = f"{days // 30} months"
            else:
                account_age = f"{days // 365} years"
        except Exception:
            account_age = "N/A"

    nickname = safe_str(basic.get('nickname'))

    text = f"""
🎮 PLAYER INFORMATION 🎮

👤 BASIC PROFILE
├─ Nickname: {nickname}
├─ UID: {uid}
├─ Region: {safe_str(basic.get('region'))}
├─ Account Type: {'Normal' if basic.get('accountType') == 1 else 'Guest'}
├─ Level: {safe_str(basic.get('level'))}
├─ Experience: {basic.get('exp', 0) or 0:,}
├─ Total Likes: {basic.get('liked', 0) or 0:,}
├─ Account Age: {account_age}
├─ Game Version: {safe_str(basic.get('releaseVersion'), 'OB')}
└─ Created At: {convert_time(basic.get('createAt'))}

🏆 RANK STATUS
├─ BR Rank: {br_rank} (Code: {safe_str(basic.get('rank'))})
├─ BR Rank Points: {basic.get('rankingPoints', 0) or 0:,}
├─ Max BR Rank: {safe_str(basic.get('maxRank'))}
├─ CS Rank: {cs_rank} (Code: {safe_str(basic.get('csRank'))})
├─ CS Rank Points: {basic.get('csRankingPoints', 0) or 0:,}
└─ Max CS Rank: {safe_str(basic.get('csMaxRank'))}

🧩 CUSTOMIZATION & ITEMS
├─ Avatar ID: {safe_str(profile.get('avatarId'))}
├─ Banner ID: {safe_str(basic.get('bannerId'))}
├─ Head Pic: {safe_str(basic.get('headPic'))}
├─ Badge ID: {safe_str(basic.get('badgeId'))}
├─ Equipped Title: {safe_str(basic.get('title'))}
├─ Pin ID: {safe_str(basic.get('pinId'))}
├─ Game Bag Show: {safe_str(basic.get('gameBagShow'))}
├─ Season ID: {safe_str(basic.get('seasonId'))}
├─ Star Player: {'Yes' if profile.get('isMarkedStar') else 'No'}
├─ PVE Weapon: {safe_str(profile.get('pvePrimaryWeapon'))}
├─ Equipped Skills: {', '.join(map(str, skills)) if skills else 'None'}
├─ Weapon Skins: {', '.join(map(str, weapons)) if weapons else 'None'}
└─ Outfits (IDs): {', '.join(map(str, clothes)) if clothes else 'None'}

🏰 CLAN DETAILS
├─ Clan Name: {safe_str(clan.get('clanName'), 'No Clan')}
├─ Clan ID: {safe_str(clan.get('clanId'))}
├─ Clan Level: {safe_str(clan.get('clanLevel'))}
├─ Members: {clan.get('memberNum', 0) or 0} / {clan.get('capacity', 0) or 0}
├─ Leader UID: {safe_str(captain.get('accountId'))}
├─ Leader Name: {safe_str(captain.get('nickname'))}
├─ Leader Level: {safe_str(captain.get('level'))}
├─ Leader Likes: {captain.get('liked', 0) or 0:,}
└─ Leader Region: {safe_str(captain.get('region'))}

🐾 COMPANION (PET)
├─ Pet ID: {safe_str(pet.get('id'))}
├─ Pet Level: {safe_str(pet.get('level'))}
├─ Pet EXP: {safe_str(pet.get('exp'), '0')}
├─ Skin ID: {safe_str(pet.get('skinId'))}
├─ Selected Skill: {safe_str(pet.get('selectedSkillId'))}
└─ Is Equipped: {'Yes' if pet.get('isSelected') else 'No'}

💬 SOCIAL PROFILE
├─ Bio Language: {safe_replace(social.get('language'), 'Language_', 'EN')}
├─ Active Time: {safe_replace(social.get('timeActive'), 'TimeActive_', 'DAY')}
├─ Signature: {safe_str(social.get('signature'), 'No Signature')}
└─ Pref. Rank Mode: {safe_replace(social.get('rankShow'), 'RankShow_', 'BR')}

💰 SYSTEM ECONOMY & TIMELINE
├─ Credit Score: {safe_str(credit.get('creditScore'), '100')}/100
├─ Est. Diamond Cost: {safe_str(diamond.get('diamondCost'))} 💎
├─ Last Login Time: {convert_time(basic.get('lastLoginAt'))}
└─ History Period End: {convert_time(credit.get('periodicSummaryEndTime'))}

Build : Developer Habib 69
Support : @DeveloperHabib69
"""
    return text


def send_long_message(chat_id, text, reply_to_message_id=None):
    if len(text) <= TELEGRAM_MAX_LEN:
        bot.send_message(chat_id, text, reply_to_message_id=reply_to_message_id)
        return

    chunks = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > TELEGRAM_MAX_LEN:
            chunks.append(current)
            current = line
        else:
            current = current + "\n" + line if current else line
    if current:
        chunks.append(current)

    for i, chunk in enumerate(chunks):
        bot.send_message(chat_id, chunk, reply_to_message_id=reply_to_message_id if i == 0 else None)


def safe_delete_message(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        logging.warning(f"Could not delete message {message_id}: {e}")


def safe_edit_message(text, chat_id, message_id):
    try:
        bot.edit_message_text(text, chat_id, message_id)
    except Exception as e:
        logging.warning(f"Could not edit message {message_id}: {e}")
        try:
            bot.send_message(chat_id, text)
        except Exception as e2:
            logging.error(f"Could not send fallback message either: {e2}")


# ================= EXECUTE ACTIONS (CORE LOGIC) =================
def execute_info_search(chat_id, user_id, uid, reply_to_message_id=None):
    """প্লেয়ারের ইনফো খোঁজার মূল প্রসেস"""
    processing = bot.send_message(chat_id, f"⏳ Accessing database... Fetching profile for UID {uid}...", reply_to_message_id=reply_to_message_id)
    try:
        url = INFO_API.format(uid=uid)
        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            safe_edit_message("❌ Database API error. Please try again in a few moments.", chat_id, processing.message_id)
            return

        try:
            data = response.json()
        except ValueError:
            safe_edit_message("❌ API parsed empty or invalid json structural response.", chat_id, processing.message_id)
            return

        if not isinstance(data, dict) or "basicInfo" not in data:
            safe_edit_message("❌ Player ID not found. Verify the Free Fire UID and re-try.", chat_id, processing.message_id)
            return

        formatted_text = format_player_info(data, uid)

        safe_delete_message(chat_id, processing.message_id)
        send_long_message(chat_id, formatted_text, reply_to_message_id=reply_to_message_id)

    except Exception as e:
        logging.error(f"Info execution critical error: {e}")
        safe_edit_message(f"❌ Internal System Error: {str(e)}", chat_id, processing.message_id)


# ================= START COMMAND =================
@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        user_name = message.from_user.first_name or "Player"

        welcome_text = f"""
✨ WELCOME {user_name.upper()} ✨

🤖 Free Fire ID INFO BOT
👨‍💻 Owner: Developer Habib 69
🛡️ Support: @DeveloperHabib69

📌 QUICK COMMAND

🚀 Use /info Your_UID

📝 Example:
/info 9032419789

🎯 Get Real-time Free Fire Player Statistics

💡 Use /help for more commands
"""
        try:
            image_response = requests.get(WELCOME_IMAGE, timeout=15)
            content_type = image_response.headers.get("Content-Type", "")
            if image_response.status_code == 200 and "image" in content_type:
                photo = BytesIO(image_response.content)
                photo.name = "welcome.png"
                bot.send_photo(message.chat.id, photo, caption=welcome_text)
            else:
                bot.reply_to(message, welcome_text)
        except Exception as e:
            logging.warning(f"Welcome image failed: {e}")
            bot.reply_to(message, welcome_text)

    except Exception as e:
        logging.error(f"Start command error: {e}")
        bot.reply_to(message, "Use /info <UID> to get player details.")


# ================= HELP COMMAND =================
@bot.message_handler(commands=['help'])
def help_command(message):
    text = """
📖 COMMAND GUIDE

/info <uid> - Get player info
/start - Welcome message
/help - Show this guide

📊 WHAT YOU GET

✅ Player Basic Info
✅ Rank Details (BR & CS)
✅ Clan Information
✅ Pet Details
✅ Social Information
✅ Account Timeline

💻 Maintained by: Developer Habib 69
🛡️ Tech Support: @DeveloperHabib69
"""
    bot.reply_to(message, text)


# ================= INFO COMMAND =================
@bot.message_handler(commands=['info'])
def info_command(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Syntax Error!\nUse: `/info <UID>`\nExample: `/info 9097982134`")
        return

    uid = parts[1].strip()
    if not uid.isdigit():
        bot.reply_to(message, "❌ Access Denied! UID must contain numbers only.")
        return

    # 🛑 FORCE JOIN CHECK
    user_id = message.from_user.id
    if not is_user_joined(user_id):
        markup = get_join_keyboard(uid, "info")
        bot.reply_to(
            message,
            "⚠️ **Access Denied!**\n\nআমাদের বটের এই সার্ভিসটি গ্রুপে সম্পূর্ণ ফ্রিতে ব্যবহার করতে হলে নিচে দেওয়া আমাদের ২টি চ্যানেলে অবশ্যই জয়েন থাকতে হবে। জয়েন করার পর **VERIFY** বাটনে ক্লিক করুন।",
            parse_mode="Markdown",
            reply_markup=markup
        )
        return

    # জয়েন থাকলে ডিরেক্ট রান হবে
    execute_info_search(message.chat.id, user_id, uid, reply_to_message_id=message.message_id)


# ================= CALLBACK QUERY HANDLER (VERIFY BUTTON) =================
@bot.callback_query_handler(func=lambda call: call.data.startswith('verify_'))
def verify_callback(call):
    user_id = call.from_user.id

    # ডাটা স্প্লিট করা (verify_commandType_uid)
    _, command_type, uid = call.data.split('_')

    # আবার চেক করুন ইউজার জয়েন করেছে কিনা
    if is_user_joined(user_id):
        # ১. জয়েন করলে প্রথমে বটের দেওয়া বাটনওয়ালা নোটিশ মেসেজটি ডিলিট করে দেবে
        safe_delete_message(call.message.chat.id, call.message.message_id)

        # টেলিগ্রামে অ্যালার্ট শো করবে যে ভেরিফিকেশন সফল
        bot.answer_callback_query(call.id, "✅ Verification Successful! Fetching data...", show_alert=False)

        # ২. এরপর অটোমেটিক মূল ইনফো দেওয়া শুরু করবে
        if command_type == "info":
            execute_info_search(call.message.chat.id, user_id, uid, reply_to_message_id=call.message.reply_to_message.message_id if call.message.reply_to_message else None)

    else:
        # জয়েন না করে চাপ দিলে নোটিফিকেশন অ্যালার্ট পপ-আপ আসবে
        bot.answer_callback_query(call.id, "❌ আপনি এখনও সব চ্যানেলে জয়েন করেননি! দয়া করে দুটি চ্যানেলেই জয়েন করে আবার ট্রাই করুন।", show_alert=True)


# ================= MAIN RUNNER =================
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 DEVELOPER HABIB 69 PLAYER INFO BOT SYSTEM")
    print("💻 Studio: Developer Habib 69")
    print("🛡️ Contact: @DeveloperHabib69")
    print("=" * 50)
    print("🤖 Bot Engine Deployment Active with Force Join...")
    print("=" * 50)

    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Polling Crash: {e}")
