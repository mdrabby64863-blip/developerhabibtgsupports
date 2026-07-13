import telebot
import requests
from datetime import datetime
from io import BytesIO
import logging

# ================= CONFIG =================
BOT_TOKEN = "8912601476:AAGeeTnJx498Xd5MP1hVrYpFkEszIG84BIM"  # ⚠️ Token shared in plain text - Regenerate via @BotFather if needed.
bot = telebot.TeleBot(BOT_TOKEN)

# ========= API LINKS =========
INFO_API = "https://nirob-x-info.vercel.app/info?uid={uid}"
OUTFIT_API = "https://nirob-free-fire-outfit.vercel.app/get?uid={uid}"
WELCOME_IMAGE = "https://freeimage.host/i/C07A0Cu"

TELEGRAM_MAX_LEN = 4096

# ========= LOGGING =========
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
╔══════════════════════════════════════╗
║    🔥🎮 PLAYER INFORMATION 🎮🔥     ║
╚══════════════════════════════════════╝

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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 RANK STATUS
├─ BR Rank: {br_rank} (Code: {safe_str(basic.get('rank'))})
├─ BR Rank Points: {basic.get('rankingPoints', 0) or 0:,}
├─ Max BR Rank: {safe_str(basic.get('maxRank'))}
├─ CS Rank: {cs_rank} (Code: {safe_str(basic.get('csRank'))})
├─ CS Rank Points: {basic.get('csRankingPoints', 0) or 0:,}
└─ Max CS Rank: {safe_str(basic.get('csMaxRank'))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐾 COMPANION (PET)
├─ Pet ID: {safe_str(pet.get('id'))}
├─ Pet Level: {safe_str(pet.get('level'))}
├─ Pet EXP: {safe_str(pet.get('exp'), '0')}
├─ Skin ID: {safe_str(pet.get('skinId'))}
├─ Selected Skill: {safe_str(pet.get('selectedSkillId'))}
└─ Is Equipped: {'Yes' if pet.get('isSelected') else 'No'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 SOCIAL PROFILE
├─ Bio Language: {safe_replace(social.get('language'), 'Language_', 'EN')}
├─ Active Time: {safe_replace(social.get('timeActive'), 'TimeActive_', 'DAY')}
├─ Signature: {safe_str(social.get('signature'), 'No Signature')}
└─ Pref. Rank Mode: {safe_replace(social.get('rankShow'), 'RankShow_', 'BR')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 SYSTEM ECONOMY & TIMELINE
├─ Credit Score: {safe_str(credit.get('creditScore'), '100')}/100
├─ Est. Diamond Cost: {safe_str(diamond.get('diamondCost'))} 💎
├─ Last Login Time: {convert_time(basic.get('lastLoginAt'))}
└─ History Period End: {convert_time(credit.get('periodicSummaryEndTime'))}

╔══════════════════════════════════════╗
║ 💻 Dev: Developer Habib 69           ║
║ 🛡️ Support: @DeveloperHabib69        ║
╚══════════════════════════════════════╝
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


# ================= START COMMAND =================
@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        user_name = message.from_user.first_name or "Player"

        welcome_text = f"""
✨ WELCOME {user_name.upper()} ✨

🤖 DEVELOPER HABIB 69 FF INFO BOT
👨‍💻 Owner: Developer Habib 69 | 🛡️ Support: @DeveloperHabib69

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 QUICK COMMAND

🚀 Use `/info <UID>` to fetch data.

📝 Example:
`/info 9097982134`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Get Real-time Free Fire Player Statistics & Outfits!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Need help? Type /help anytime.
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
📖 BOT COMMAND GUIDE

⚡ /info <uid> - Fetch comprehensive player stats
👕 /outfit <uid> - Get an instant outfit preview avatar
🔄 /start - Relaunch welcome dashboard
❓ /help - Open this documentation guide

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 EXTRACTED DATA INCLUDES:

✅ Basic Profile & Account Age
✅ Current Rank Tiers (BR & CS Modes)
✅ Active Clan Info & Leader Details
✅ Pet Equipped Stats
✅ Custom Bio Signatures
✅ Real-time Credit Score & Diamond History
✅ Virtual Outfit Rendering

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

    processing = bot.reply_to(message, f"⏳ Accessing database... Fetching profile for UID {uid}...")

    try:
        url = INFO_API.format(uid=uid)
        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            safe_edit_message("❌ Database API error. Please try again in a few moments.", message.chat.id, processing.message_id)
            return

        try:
            data = response.json()
        except ValueError:
            safe_edit_message("❌ API parsed empty or invalid json structural response.", message.chat.id, processing.message_id)
            return

        if not isinstance(data, dict) or "basicInfo" not in data:
            safe_edit_message("❌ Player ID not found. Verify the Free Fire UID and re-try.", message.chat.id, processing.message_id)
            return

        formatted_text = format_player_info(data, uid)

        safe_delete_message(message.chat.id, processing.message_id)
        send_long_message(message.chat.id, formatted_text, reply_to_message_id=message.message_id)

        try:
            outfit_url = OUTFIT_API.format(uid=uid)
            outfit_response = requests.get(outfit_url, timeout=30)

            if outfit_response.status_code == 200:
                photo = BytesIO(outfit_response.content)
                photo.name = "outfit.png"
                nickname = (data.get("basicInfo") or {}).get("nickname", "Unknown")
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption=f"👕 Outfit Rendered\n🎮 {nickname} | 🆔 {uid}",
                    reply_to_message_id=message.message_id
                )
        except Exception as e:
            logging.warning(f"Outfit auto-fetch omitted/failed for uid {uid}: {e}")

    except Exception as e:
        logging.error(f"Info command critical error: {e}")
        safe_edit_message(f"❌ Internal System Error: {str(e)}", message.chat.id, processing.message_id)


# ================= OUTFIT COMMAND =================
@bot.message_handler(commands=['outfit'])
def outfit_command(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Syntax Error!\nUse: `/outfit <UID>`\nExample: `/outfit 9097982134`")
        return

    uid = parts[1].strip()
    if not uid.isdigit():
        bot.reply_to(message, "❌ Access Denied! UID must contain numbers only.")
        return

    processing = bot.reply_to(message, f"⏳ Rendering player avatar cosmetics for UID {uid}...")

    try:
        outfit_url = OUTFIT_API.format(uid=uid)
        response = requests.get(outfit_url, timeout=30)

        if response.status_code != 200:
            safe_edit_message("❌ Custom skin compilation failed or asset server offline.", message.chat.id, processing.message_id)
            return

        photo = BytesIO(response.content)
        photo.name = "outfit.png"

        safe_delete_message(message.chat.id, processing.message_id)
        bot.send_photo(
            message.chat.id,
            photo,
            caption=f"👕 Outfit Preview Model\n🆔 UID Account Reference: {uid}",
            reply_to_message_id=message.message_id
        )

    except Exception as e:
        logging.error(f"Outfit interface error: {e}")
        safe_edit_message(f"❌ Execution Fault: {str(e)}", message.chat.id, processing.message_id)


# ================= MAIN RUNNER =================
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 DEVELOPER HABIB 69 PLAYER INFO BOT SYSTEM")
    print("💻 Dev Studio: Developer Habib 69")
    print("🛡️ Contact: @DeveloperHabib69")
    print("=" * 50)
    print("🤖 Bot Engine Deployment Active...")
    print("=" * 50)

    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Polling Crash: {e}")
