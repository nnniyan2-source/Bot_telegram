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