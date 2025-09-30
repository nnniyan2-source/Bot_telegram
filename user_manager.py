import json
import os
import re
from datetime import datetime
from telegram import User

class UserManager:
    def __init__(self, filename="users.json"):
        # Validasi filename
        if not re.match(r'^[\w\.-]+\.json$', filename):
            raise ValueError("Invalid filename")
        self.filename = filename
        self.users = self.load_users()
    
    def sanitize_input(self, text, max_length=1000):
        """Sanitize input text untuk mencegah injeksi"""
        if text is None:
            return ""
        
        # Batasi panjang
        text = str(text)[:max_length]
        
        # Hapus karakter berbahaya untuk JSON
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)  # Hapus control characters
        text = text.replace('\\', '\\\\').replace('"', '\\"')  # Escape karakter
        
        return text
    
    def validate_user_id(self, user_id):
        """Validasi user_id"""
        if isinstance(user_id, (int, str)):
            user_id_str = str(user_id)
            if user_id_str.isdigit() and len(user_id_str) <= 20:
                return user_id_str
        return None
    
    def load_users(self):
        """Load data pengguna dari file JSON dengan security"""
        try:
            if os.path.exists(self.filename):
                # Cek file size (max 10MB)
                if os.path.getsize(self.filename) > 10 * 1024 * 1024:
                    print("❌ File terlalu besar!")
                    return {}
                
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Validasi structure data
                    if isinstance(data, dict):
                        # Sanitize semua data
                        sanitized_data = {}
                        for user_id, user_data in data.items():
                            if self.validate_user_id(user_id) and isinstance(user_data, dict):
                                sanitized_data[user_id] = self.sanitize_user_data(user_data)
                        return sanitized_data
                    return {}
            return {}
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"❌ Error loading users (corrupted file): {e}")
            # Backup file yang corrupt
            self.backup_corrupted_file()
            return {}
        except Exception as e:
            print(f"❌ Error loading users: {e}")
            return {}
    
    def sanitize_user_data(self, user_data):
        """Sanitize data user individual"""
        sanitized = {}
        
        # Field yang diizinkan
        allowed_fields = {
            'id', 'first_name', 'username', 'language_code', 
            'first_seen', 'last_seen', 'message_count', 
            'total_messages', 'last_message', 'premium', 
            'premium_since', 'credits'
        }
        
        for field, value in user_data.items():
            if field in allowed_fields:
                if field in ['first_name', 'username', 'last_message']:
                    sanitized[field] = self.sanitize_input(value, 500)
                elif field in ['first_seen', 'last_seen', 'premium_since']:
                    # Validasi format datetime ISO
                    if isinstance(value, str) and re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value):
                        sanitized[field] = value
                elif field in ['id', 'message_count', 'total_messages', 'credits']:
                    # Validasi angka
                    if isinstance(value, (int, float)) and value >= 0:
                        sanitized[field] = int(value)
                elif field == 'premium':
                    # Validasi boolean
                    sanitized[field] = bool(value)
                elif field == 'language_code':
                    # Validasi language code
                    if isinstance(value, str) and re.match(r'^[a-z]{2,3}(-[A-Z]{2,3})?$', value):
                        sanitized[field] = value
        
        return sanitized
    
    def backup_corrupted_file(self):
        """Backup file yang corrupt"""
        try:
            if os.path.exists(self.filename):
                backup_name = f"{self.filename}.corrupted.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.filename, backup_name)
                print(f"📦 File corrupt dibackup sebagai: {backup_name}")
        except Exception as e:
            print(f"❌ Gagal backup file corrupt: {e}")
    
    def save_users(self):
        """Simpan data pengguna ke file JSON dengan security"""
        try:
            # Validasi data sebelum save
            if not isinstance(self.users, dict):
                print("❌ Invalid data structure!")
                return
            
            # Limit jumlah users (prevent memory exhaustion)
            if len(self.users) > 100000:
                print("❌ Too many users!")
                return
            
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving users: {e}")
    
    def add_or_update_user(self, telegram_user: User, message_text=None):
        """Tambah atau update data pengguna dengan security"""
        user_id = self.validate_user_id(telegram_user.id)
        if not user_id:
            print(f"❌ Invalid user ID: {telegram_user.id}")
            return None
        
        # Sanitize input
        sanitized_message = self.sanitize_input(message_text, 500)
        sanitized_first_name = self.sanitize_input(telegram_user.first_name, 100)
        sanitized_username = self.sanitize_input(telegram_user.username, 100)
        
        if user_id not in self.users:
            # User baru
            self.users[user_id] = {
                'id': telegram_user.id,
                'first_name': sanitized_first_name,
                'username': sanitized_username,
                'language_code': self.sanitize_input(telegram_user.language_code, 10),
                'first_seen': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat(),
                'message_count': 1,
                'total_messages': 1,
                'last_message': sanitized_message,
                'premium': False,
                'premium_since': None,
                'credits': 0
            }
            print(f"👤 User baru ditambahkan: {sanitized_first_name} (ID: {user_id})")
        else:
            # Update user yang sudah ada
            self.users[user_id]['last_seen'] = datetime.now().isoformat()
            self.users[user_id]['message_count'] += 1
            self.users[user_id]['total_messages'] += 1
            self.users[user_id]['last_message'] = sanitized_message
            
            # Update info jika ada perubahan
            self.users[user_id]['first_name'] = sanitized_first_name
            self.users[user_id]['username'] = sanitized_username
        
        # Auto-save ke file
        self.save_users()
        
        return self.users[user_id]
    
    def set_premium(self, user_id, premium_status=True):
        """Set status premium user dengan security"""
        user_id = self.validate_user_id(user_id)
        if not user_id or user_id not in self.users:
            return False
        
        # Validasi input
        premium_status = bool(premium_status)
        
        self.users[user_id]['premium'] = premium_status
        if premium_status:
            self.users[user_id]['premium_since'] = datetime.now().isoformat()
        else:
            self.users[user_id]['premium_since'] = None
        
        self.save_users()
        return True
    
    def is_premium(self, user_id):
        """Cek apakah user premium dengan security"""
        user_id = self.validate_user_id(user_id)
        if not user_id or user_id not in self.users:
            return False
        
        return self.users[user_id].get('premium', False)
    
    # FUNGSI YANG DITAMBAHKAN:
    
    def get_premium_users(self):
        """Ambil semua user premium"""
        premium_users = []
        for user_id, data in self.users.items():
            if data.get('premium', False):
                premium_users.append({
                    'id': user_id,
                    'name': data.get('first_name', 'Unknown'),
                    'username': data.get('username', 'No username'),
                    'premium_since': data.get('premium_since', 'Unknown')
                })
        return premium_users
    
    def add_credits(self, user_id, amount):
        """Tambah credits ke user dengan security"""
        user_id = self.validate_user_id(user_id)
        if not user_id or user_id not in self.users:
            return None
        
        # Validasi amount
        if not isinstance(amount, (int, float)) or amount < 0:
            return None
        
        self.users[user_id]['credits'] = self.users[user_id].get('credits', 0) + amount
        self.save_users()
        return self.users[user_id]['credits']
    
    def deduct_credits(self, user_id, amount):
        """Kurangi credits user dengan security"""
        user_id = self.validate_user_id(user_id)
        if not user_id or user_id not in self.users:
            return None
        
        # Validasi amount
        if not isinstance(amount, (int, float)) or amount < 0:
            return None
        
        current_credits = self.users[user_id].get('credits', 0)
        if current_credits >= amount:
            self.users[user_id]['credits'] = current_credits - amount
            self.save_users()
            return self.users[user_id]['credits']
        return None
    
    def get_user_stats(self, user_id):
        """Ambil statistik pengguna"""
        user_id = self.validate_user_id(user_id)
        if not user_id or user_id not in self.users:
            return None
        return self.users[user_id]
    
    def get_all_users(self):
        """Ambil semua data pengguna"""
        return self.users
    
    def get_total_users(self):
        """Hitung total pengguna unik"""
        return len(self.users)
    
    def get_top_users(self, limit=10):
        """Ambil top users berdasarkan jumlah pesan"""
        users_list = []
        for user_id, data in self.users.items():
            users_list.append({
                'id': user_id,
                'name': data.get('first_name', 'Unknown'),
                'username': data.get('username', 'No username'),
                'total_messages': data.get('total_messages', 0),
                'first_seen': data.get('first_seen', 'Unknown'),
                'premium': data.get('premium', False)
            })
        
        # Urutkan berdasarkan total messages (descending)
        users_list.sort(key=lambda x: x['total_messages'], reverse=True)
        return users_list[:limit]