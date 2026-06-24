import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Load variabel dari file .env
load_dotenv()

# Ambil otomatis tanpa perlu input manual
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

def main():
    print("=== GENERATOR STRING SESSION TELETHON ===")
    print("Membaca API_ID dan API_HASH dari .env...\n")
    print("Siapkan nomor HP (dengan kode negara, misal: +62812...) dan buka Telegram Anda.\n")
    
    # Langsung konek pakai kredensial dari environment
    with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        print("\n✅ BERHASIL LOGIN!")
        print("======================================================")
        print("Berikut adalah String Session Anda (Copy teks panjang di bawah ini):\n")
        
        session_string = client.session.save()
        print(session_string)
        
        print("\n======================================================")

if __name__ == '__main__':
    main()