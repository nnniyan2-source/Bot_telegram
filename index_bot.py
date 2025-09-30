import json
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update

# Import handler functions dari main_bot.py
from main_bot import handle_start_command, handle_command_message, handle_normal_message

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        self.updaters = []
        
    def load_tokens(self):
        """Load tokens dari file JSON"""
        try:
            with open('token.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_tokens(self, tokens):
        """Simpan tokens ke file JSON"""
        with open('token.json', 'w') as f:
            json.dump(tokens, f, indent=2)
    
    def setup_bot_handlers(self, updater):
        """Setup semua handlers untuk satu bot"""
        dp = updater.dispatcher
        
        # Command handlers
        dp.add_handler(CommandHandler("start", handle_start_command))
        
        # Message handlers - priority: command dulu, lalu normal message
        dp.add_handler(MessageHandler(Filters.text, handle_command_message))
        dp.add_handler(MessageHandler(Filters.text, handle_normal_message))
        
        # Error handler
        dp.add_error_handler(self.error_handler)
    
    def error_handler(self, update, context):
        """Global error handler - PARAMETER DIPERBAIKI"""
        logger.error(f"Error: {context.error}")
    
    def setup_bots(self, tokens):
        """Setup semua bot dari list tokens"""
        for token in tokens:
            try:
                # Gunakan Updater dengan use_context=True untuk versi baru
                updater = Updater(token, use_context=True)
                
                # Setup handlers untuk bot ini
                self.setup_bot_handlers(updater)
                
                self.updaters.append(updater)
                print(f"✅ Bot dengan token {token[:10]}... berhasil di setup!")
                
            except Exception as e:
                print(f"❌ Error setup bot {token[:10]}: {e}")
    
    def start_all(self):
        """Mulai semua bot"""
        print("🚀 Memulai semua bot...")
        for updater in self.updaters:
            try:
                updater.start_polling()
                print(f"📡 Bot {updater.bot.token[:10]}... mulai polling!")
            except Exception as e:
                print(f"❌ Error starting bot: {e}")
        
        # Keep the program running
        print("\n" + "="*50)
        print("✅ Semua bot berjalan!")
        print("⏹️  Tekan Ctrl+C untuk berhenti")
        print("="*50)
        
        # Idle untuk menjaga bot tetap running
        for updater in self.updaters:
            updater.idle()

def main():
    """Main function"""
    manager = BotManager()
    
    # Load existing tokens
    tokens = manager.load_tokens()
    
    print("🤖 Multi-Bot Manager")
    print("=" * 30)
    
    # Jika belum ada tokens, minta input pertama
    if not tokens:
        print("Belum ada token yang terdaftar.")
        new_token = input("Masukkan token bot pertama: ").strip()
        if new_token:
            tokens.append(new_token)
            manager.save_tokens(tokens)
            print("✅ Token berhasil disimpan!")
    
    # Tampilkan tokens yang ada
    if tokens:
        print(f"\n📋 Tokens terdaftar ({len(tokens)} bot):")
        for i, token in enumerate(tokens, 1):
            print(f"  {i}. {token[:10]}...")
    
    # Tanya mau tambah token baru atau tidak
    while True:
        choice = input("\n➕ Tambah bot baru? (y/n): ").lower().strip()
        if choice == 'y':
            new_token = input("Masukkan token bot baru: ").strip()
            if new_token:
                if new_token not in tokens:
                    tokens.append(new_token)
                    manager.save_tokens(tokens)
                    print("✅ Token berhasil ditambahkan!")
                else:
                    print("❌ Token sudah terdaftar!")
        else:
            break
    
    # Setup dan start semua bot
    if tokens:
        print(f"\n🔄 Setting up {len(tokens)} bot...")
        manager.setup_bots(tokens)
        manager.start_all()
    else:
        print("❌ Tidak ada bot yang bisa dijalankan!")

if __name__ == "__main__":
    main()