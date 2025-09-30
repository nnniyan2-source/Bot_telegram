🤖 Multi-Bot Telegram Manager

Bot Telegram yang dapat mengelola multiple bot sekaligus dengan fitur user management, premium system, dan security features.

📋 Fitur

· ✅ Multi-bot Support - Jalankan banyak bot sekaligus
· ✅ User Management - Auto-save data pengguna ke JSON
· ✅ Premium System - Sistem premium user dengan creditsn
· ✅ Security Features - Input validation & sanitization
· ✅ Command System - Prefix-based commands dengan logging
· ✅ Rate Limiting - Mencegah spam
· ✅ Error Handling - Comprehensive error management

🚀 Instalasi

1. Clone Repository

```bash
# Clone dari GitHub
git clone https://github.com/username/multi-bot-telegram.git
cd multi-bot-telegram

# Atau download manual dan extract
```

2. Install Dependencies

```bash
pip install python-telegram-bot python-dotenv
```

3. Setup Environment

Buat file .env:

```env
BOT_TOKEN=your_bot_token_here
BOT_USERNAME=@YourBotUsername
```

4. Konfigurasi

Edit config.py:

```python
# Ganti dengan ID Telegram kamu
OWNER_ID = 123456789
```

🛠️ Penyelesaian Masalah

Masalah: ImportError: cannot import name 'imghdr'

Problem: Python 3.13+ menghapus module imghdr yang dibutuhkan python-telegram-bot.

Solusi: Jalankan script patch:

```bash
python fix_imghdr.py
```

File fix_imghdr.py

```python
import os
import sys

def patch_telegram_bot():
    """Patch python-telegram-bot untuk handle missing imghdr"""
    
    # Path ke file inputfile.py
    telegram_path = os.path.join(os.path.dirname(os.__file__), 'site-packages', 'telegram', 'files', 'inputfile.py')
    
    try:
        with open(telegram_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace import imghdr
        old_import = "import imghdr"
        new_import = """try:
    import imghdr
except ImportError:
    # Fallback untuk Python 3.13+ yang tidak punya imghdr
    imghdr = None
    import mimetypes"""
        
        content = content.replace(old_import, new_import)
        
        # Replace _is_image function
        old_function = '''def _is_image(filelike: BinaryIO) -> bool:
    """
    Check if the filelike object contains image data.

    Args:
        filelike: The filelike object to check.

    Returns:
        bool: True if the filelike object contains image data.
    """
    filelike.seek(0)
    image_type = imghdr.what(filelike)
    filelike.seek(0)
    return image_type is not None'''
        
        new_function = '''def _is_image(filelike: BinaryIO) -> bool:
    """
    Check if the filelike object contains image data.

    Args:
        filelike: The filelike object to check.

    Returns:
        bool: True if the filelike object contains image data.
    """
    if imghdr is not None:
        # Gunakan imghdr jika available
        filelike.seek(0)
        image_type = imghdr.what(filelike)
        filelike.seek(0)
        return image_type is not None
    else:
        # Fallback menggunakan mimetypes dan magic bytes
        filelike.seek(0)
        header = filelike.read(1024)
        filelike.seek(0)
        
        # Deteksi image dari magic bytes
        if header.startswith(b'\\xff\\xd8\\xff'):
            return True  # JPEG
        elif header.startswith(b'\\x89PNG\\r\\n\\x1a\\n'):
            return True  # PNG
        elif header.startswith(b'GIF8'):
            return True  # GIF
        elif header.startswith(b'BM'):
            return True  # BMP
        elif header.startswith(b'\\x00\\x00\\x01\\x00'):
            return True  # ICO
        elif header.startswith(b'RIFF') and header[8:12] == b'WEBP':
            return True  # WEBP
        
        return False'''
        
        content = content.replace(old_function, new_function)
        
        # Write back
        with open(telegram_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Patch berhasil! python-telegram-bot sekarang compatible dengan Python 3.13")
        return True
        
    except Exception as e:
        print(f"❌ Patch gagal: {e}")
        return False

# Jalankan patch
if patch_telegram_bot():
    print("\nSekarang bisa menjalankan kode bot dengan python-telegram-bot!")
else:
    print("\nPatch gagal, gunakan alternatif lain")
```

Alternatif jika Patch Gagal

```bash
# Install versi python-telegram-bot yang lebih tua
pip uninstall python-telegram-bot
pip install python-telegram-bot==13.15

# Atau install backport imghdr
pip install imghdr-backport
```

🏃‍♂️ Menjalankan Bot

Mode Single Bot

```bash
python main_bot.py
```

Mode Multi-Bot Manager

```bash
python index_bot.py
```

📁 Struktur Project

```
multi-bot-telegram/
├── 📄 index_bot.py          # Multi-bot manager
├── 📄 main_bot.py           # Command handlers
├── 📄 user_manager.py       # User management system
├── 📄 config.py            # Configuration
├── 📄 fix_imghdr.py        # Patch untuk Python 3.13+
├── 📄 .env                 # Environment variables
├── 📄 token.json           # Bot tokens storage
├── 📄 users.json           # User data (auto-generated)
└── 📄 README.md            # Documentation
```

⌨️ Daftar Perintah

User Commands

· /start - Memulai bot
· !help - Menampilkan bantuan
· !test - Test bot response
· !info - Info bot
· !stats - Statistik user
· !myid - Lihat ID Telegram
· !premium - Cek status premium

Owner Commands

· !topusers - Top 10 pengguna
· !setpremium <user_id> - Set user premium
· !premiumlist - List user premium

🔧 Troubleshooting

Error: Token tidak ditemukan

· Pastikan file .env sudah dibuat
· Format: BOT_TOKEN=your_token_here

Error: AttributeError: 'CallbackContext'

· Gunakan parameter (update, context) bukan (bot, update)
· Pastikan menggunakan use_context=True

Error: File users.json corrupt

· File akan otomatis dibackup
· Data baru akan dibuat otomatis

Error: Too many requests

· Rate limiting aktif (20 requests per menit)
· Tunggu beberapa saat sebelum request lagi

🛡️ Security Features

· ✅ Input validation & sanitization
· ✅ JSON injection protection
· ✅ Rate limiting
· ✅ File size limits
· ✅ Data structure validation
· ✅ Backup system for corrupted files

📊 Data Storage

users.json

```json
{
  "123456789": {
    "id": 123456789,
    "first_name": "John",
    "username": "johndoe",
    "premium": true,
    "premium_since": "2024-01-15T10:30:00",
    "credits": 100,
    "total_messages": 50
  }
}
```

token.json

```json
[
  "token1_here",
  "token2_here"
]
```

🤝 Kontribusi

1. Fork repository
2. Buat feature branch (git checkout -b feature/AmazingFeature)
3. Commit changes (git commit -m 'Add AmazingFeature')
4. Push branch (git push origin feature/AmazingFeature)
5. Buat Pull Request

📝 License

Distributed under the MIT License. See LICENSE for more information.

📞 Support

Jika mengalami masalah:

1. Cek section Troubleshooting di atas
2. Pastikan semua dependencies terinstall
3. Jalankan fix_imghdr.py jika menggunakan Python 3.13+
4. Buat issue di GitHub repository

---

Happy Coding! 🚀
