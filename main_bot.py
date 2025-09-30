from config import PREFIX, OWNER_ID
from datetime import datetime
from user_manager import UserManager

# Inisialisasi UserManager
user_manager = UserManager()

def is_user_premium(user_id):
    """Cek apakah user premium - PENgecekan dilakukan di sini"""
    return user_manager.is_premium(user_id)

def log_command(user_id, text, filter_status=None):
    """Logging command dengan warna dan format yang keren"""
    now = datetime.now().strftime("%H:%M:%S") 
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    PURPLE = "\033[95m"
    RESET = "\033[0m"
    WHITE = "\033[97m"
    YELLOW = "\033[93m"
    LINE = f"{PURPLE}━━━━━━━━━━━━━━━━━━━━━━━{RESET}"
    
    # Cek status premium di sini
    if user_id == OWNER_ID:
        status_cek = "👑 Ownerr"
    elif is_user_premium(user_id):
        status_cek = "✅ Premium"
    else:
        status_cek = "❌ Bukan Premium"
    
    print(LINE)
    print(f"{CYAN}❗ MENERIMA PERINTAH{WHITE}({now}){RESET}")
    print(f"{YELLOW}[ID] User   : {user_id}{RESET}")
    print(f"{GREEN} Status : {status_cek}{RESET} ")
    print(f"{GREEN}[MSG] Pesan  : {text}{RESET}")
    if filter_status is not None:
        print(f"{PURPLE}🔍 Filter : {filter_status}{RESET}")
    print(LINE)

def handle_start_command(update, context):
    """Handler untuk /start"""
    user = update.message.from_user
    user_id = user.id
    
    # Simpan/update user data
    user_data = user_manager.add_or_update_user(user, "/start")
    
    log_command(user_id, "/start", "Start Command")
    
    # Cek status premium untuk welcome message
    premium_status = "✅ Premium User" if is_user_premium(user_id) else "❌ Regular User"
    
    welcome_text = f"""
👋 **Selamat Datang {user.first_name}!**

📊 **Statistik Anda:**
🆔 ID: `{user_id}`
📛 Status: {premium_status}
📨 Total Pesan: {user_data['total_messages']}
💰 Credits: {user_data.get('credits', 0)}
📅 Bergabung: {user_data['first_seen'][:10]}

Gunakan prefix `{PREFIX}` di depan perintah.

Contoh:
`{PREFIX}test` - Test bot
`{PREFIX}help` - Bantuan
`{PREFIX}stats` - Statistik Anda

Bot siap melayani!
"""
    update.message.reply_text(welcome_text, parse_mode='Markdown')

def handle_command_message(update, context):
    """Main handler untuk semua command dengan prefix"""
    text = update.message.text
    user = update.message.from_user
    user_id = user.id
    
    # Cek apakah pesan diawali prefix
    if not text.startswith(PREFIX):
        return  # Langsung skip jika tidak ada prefix
    
    # Simpan/update user data
    user_data = user_manager.add_or_update_user(user, text)
    if command == "p":
        update.message.reply_text(f"Prefix : {PREFIX}")
    # Log command
    log_command(user_id, text, "Prefix Command")
    
    # Ambil command setelah prefix
    command = text[len(PREFIX):].strip().lower()
    
    # Handle command dengan if statement
    elif command == "test":
        update.message.reply_text("🏓 Pong!")
    
    elif command == "menu":
        help_text = f"""
🤖 **Daftar Perintah:**
`{PREFIX}test` - Test bot response
`{PREFIX}menu` - Menampilkan bantuan
`{PREFIX}info` - Info bot
`{PREFIX}time` - Waktu sekarang
`{PREFIX}ping` - Test ping
`{PREFIX}stats` - Statistik Anda
`{PREFIX}myid` - Lihat ID Anda
`{PREFIX}premium` - Cek status premium

**👑 Owner Commands:**
`{PREFIX}topusers` - Top 10 pengguna
`{PREFIX}setpremium` - Set user premium
`{PREFIX}premiumlist` - List user premium
"""
        update.message.reply_text(help_text, parse_mode='Markdown')
    
    elif command == "info":
        total_users = user_manager.get_total_users()
        premium_users = len(user_manager.get_premium_users())
        info_text = f"""
ℹ️ **Bot Information**
- Name: Multi-Bot Manager
- Version: 2.0
- Prefix: {PREFIX}
- Status: Active
- Total Users: {total_users}
- Premium Users: {premium_users}
- Your ID: {user_id}
"""
        update.message.reply_text(info_text, parse_mode='Markdown')
    
    elif command == "ping":
        update.message.reply_text("Pong! 🎯")
    
    elif command == "time":
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update.message.reply_text(f"🕐 Waktu sekarang: {now}")
    
    elif command == "myid":
        update.message.reply_text(f"🆔 Your Telegram ID: `{user_id}`", parse_mode='Markdown')
    
    elif command == "premium":
        if is_user_premium(user_id):
            user_data = user_manager.get_user_stats(user_id)
            premium_since = user_data.get('premium_since', 'Unknown')[:10] if user_data.get('premium_since') else 'Unknown'
            update.message.reply_text(f"🎉 **Anda adalah Premium User!**\n📅 Sejak: {premium_since}", parse_mode='Markdown')
        else:
            update.message.reply_text("❌ **Anda bukan Premium User**\nHubungi owner untuk upgrade!", parse_mode='Markdown')
    
    elif command == "stats":
        user_data = user_manager.get_user_stats(user_id)
        if user_data:
            premium_status = "✅ Premium" if user_data.get('premium', False) else "❌ Regular"
            stats_text = f"""
📊 **Statistik {user.first_name}**

🆔 ID: `{user_id}`
👤 Username: @{user_data.get('username', 'No username')}
📛 Status: {premium_status}
📨 Total Pesan: {user_data.get('total_messages', 0)}
💰 Credits: {user_data.get('credits', 0)}
📅 Bergabung: {user_data.get('first_seen', 'Unknown')[:10]}
⏰ Terakhir Online: {user_data.get('last_seen', 'Unknown')[:16]}
"""
            update.message.reply_text(stats_text, parse_mode='Markdown')
        else:
            update.message.reply_text("❌ Data tidak ditemukan!")
    
    # OWNER COMMANDS
    elif command == "topusers" and user_id == OWNER_ID:
        top_users = user_manager.get_top_users(10)
        top_text = "🏆 **TOP 10 PENGGUNA**\n\n"
        for i, user_data in enumerate(top_users, 1):
            premium_badge = "👑" if user_data['premium'] else ""
            top_text += f"{i}. {user_data['name']} (@{user_data['username']}) {premium_badge}\n"
            top_text += f"   📨 {user_data['total_messages']} pesan\n"
            top_text += f"   📅 {user_data['first_seen'][:10]}\n\n"
        update.message.reply_text(top_text, parse_mode='Markdown')
    
    elif command.startswith("setpremium") and user_id == OWNER_ID:
        # !setpremium 123456789
        parts = text.split()
        if len(parts) >= 2:
            target_user_id = int(parts[1])
            if user_manager.set_premium(target_user_id, True):
                update.message.reply_text(f"✅ User {target_user_id} sekarang Premium!")
            else:
                update.message.reply_text("❌ User tidak ditemukan!")
        else:
            update.message.reply_text("❌ Format: !setpremium <user_id>")
    
    elif command == "premiumlist" and user_id == OWNER_ID:
        premium_users = user_manager.get_premium_users()
        if premium_users:
            premium_text = "👑 **PREMIUM USERS**\n\n"
            for i, user_data in enumerate(premium_users, 1):
                premium_text += f"{i}. {user_data['name']} (@{user_data['username']})\n"
                premium_text += f"   📅 Premium sejak: {user_data['premium_since'][:10]}\n\n"
            update.message.reply_text(premium_text, parse_mode='Markdown')
        else:
            update.message.reply_text("❌ Belum ada premium users!")
    
    else:
        # Command tidak dikenali
        update.message.reply_text(f"❌ Command `{command}` tidak dikenali. Ketik `{PREFIX}help` untuk bantuan.", parse_mode='Markdown')

def handle_normal_message(update, context):
    """Handler untuk pesan normal tanpa prefix"""
    text = update.message.text
    user = update.message.from_user
    user_id = user.id
    
    # Simpan/update user data untuk pesan normal juga
    user_manager.add_or_update_user(user, text)
    
    update.message.reply_text(f"Anda mengatakan: {text}")