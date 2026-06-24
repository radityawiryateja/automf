import asyncio
import os
import re
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ==========================================
# 1. KONFIGURASI 
# ==========================================
load_dotenv()

try:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    # Kita cuma butuh 1 akun sekarang!
    SESSION = os.getenv("UBOT2_SESSION")
except Exception as e:
    print(f"[❌ FATAL ERROR] Cek lagi file .env kamu: {e}")
    exit(1)

TEMPLATES = {
    "1": "('HIT-ME-UP, @Hughtons / @Apolisebot') IDR, 58.000 / 1 MONTH via login. “FAST RESPON, FAST PROSES &. ANTI LIMIT” I, check t.me/mirezae | @testlucs (1,4k+) testimonial. 🫀",
    "1b": "('HIT-ME-UP, @.Hughtons / @.Apolisebot') IDR, 58.000 / 1 MONTH via login. “FAST RESPON, FAST PROSES &. ANTI LIMIT” I, check t.me/mirezae | @testlucs (1,4k+) testimonial. 🫀",
    "3l": "('HIT-ME-UP, @Hughtons / @Apolisebot') IDR, 174.000 / 3 MONTH via login. “FAST RESPON, FAST PROSES &. ANTI LIMIT” I, check t.me/mirezae | @testlucs (1,4k+) testimonial. 🫀",
    "3lb": "('HIT-ME-UP, @.Hughtons / @.Apolisebot') IDR, 174.000 / 3 MONTH via login. “FAST RESPON, FAST PROSES &. ANTI LIMIT” I, check t.me/mirezae | @testlucs (1,4k+) testimonial. 🫀",
    "3g": "('HIT-ME-UP, @Hughtons / @Apolisebot') IDR, 210.000 / 3 MONTH via gift. “FAST RESPON, FAST PROSES &. ANTI LIMIT” I, check t.me/mirezae | @testlucs (1,4k+) testimonial. 🫀",
    "3gb": "('HIT-ME-UP, @.Hughtons / @.Apolisebot') IDR, 210.000 / 3 MONTH via gift. “FAST RESPON, FAST PROSES &. ANTI LIMIT” I, check t.me/mirezae | @testlucs (1,4k+) testimonial. 🫀",
    "6": "('HIT-ME-UP, @Hughtons / @Apolisebot') IDR, 275.000 / 6 MONTH via gift. “FAST RESPON, FAST PROSES &. ANTI LIMIT” I, check t.me/mirezae | @testlucs (1,4k+) testimonial. 🫀",
    "6b": "('HIT-ME-UP, @Hughtons / @Apolisebot') IDR, 275.000 / 6 MONTH via gift. “FAST RESPON, FAST PROSES &. ANTI LIMIT” I, check t.me/mirezae | @testlucs (1,4k+) testimonial. 🫀",
    "1yl": "('HIT-ME-UP, @Hughtons / @Apolisebot') IDR, 375.000 / 1 YEAR via login. “FAST RESPON, FAST PROSES &. ANTI LIMIT” I, check t.me/mirezae | @testlucs (1,4k+) testimonial. 🫀",
    "1ylb": "('HIT-ME-UP, @.Hughtons / @.Apolisebot') IDR, 375.000 / 1 YEAR via login. “FAST RESPON, FAST PROSES &. ANTI LIMIT” I, check t.me/mirezae | @testlucs (1,4k+) testimonial. 🫀",
    "1yg": "('HIT-ME-UP, @Hughtons / @Apolisebot') IDR, 495.000 / 1 YEAR via gift. “FAST RESPON, FAST PROSES &. ANTI LIMIT” I, check t.me/mirezae | @testlucs (1,4k+) testimonial. 🫀",
    "1ygb": "('HIT-ME-UP, @.Hughtons / @.Apolisebot') IDR, 495.000 / 1 YEAR via gift. “FAST RESPON, FAST PROSES &. ANTI LIMIT” I, check t.me/mirezae | @testlucs (1,4k+) testimonial. 🫀",
    "d": ".☘︎ ݁˖ hurl me a halo! mampir @decavstore / @decavbot yuk, avail custom sesuai budget. rnk t.me/decavstore/766 ‘&. and our results here @decavis.",
    "a": "𖤝 Get in touch @.apolisebot / @apolise! All high-quality results ‘&. rush orders, all tailored to fit your budget. Results: @saumple / Ready: t.me/apollise/11",
    "s": "('HIT-ME-UP, @Hughtons / @Apolisebot') Stars via gift & top up start 5,1k/15s, 17k/50s, 34k/100s. “FAST RESPON &. PROSES” I, check check t.me/testlucs | @mirezae (1,4k+) testimonial. 🫀",
    "m": "Get in touch with @micedoobot for top-tier, adorable manips! Through @micedoo, custom request and rush order are open. ☆ t.me/micedoo/5066: For exploring our pre-made edits. ⌨💐"
}

CLIENT_PARAMS = {"use_ipv6": False, "timeout": 30, "connection_retries": 10}
ubot = TelegramClient(StringSession(SESSION), API_ID, API_HASH, **CLIENT_PARAMS)

# ==========================================
# 2. LOGIKA AUTO-REPLACE (REGEX)
# ==========================================
# Menyusun kunci template berdasarkan panjang kata agar yang panjang terbaca duluan (misal /1ylb tidak tertukar dengan /1)
keys_sorted = sorted(TEMPLATES.keys(), key=len, reverse=True)

# Regex ini mencari kata berawalan garis miring (/) yang ada di daftar template.
# (?<!\S) memastikan /a tidak ikut ke-replace kalau ada di dalam link (misal t.me/a)
PATTERN = r'(?i)(?<!\S)\/(' + '|'.join(keys_sorted) + r')\b'

# Fungsi ini hanya aktif untuk pesan KELUAR (yang kamu ketik sendiri)
@ubot.on(events.NewMessage(outgoing=True))
async def auto_replace_handler(event):
    try:
        if not event.text:
            return

        original_text = event.text
        
        # Cek apakah ada command template di dalam chat kita
        if re.search(PATTERN, original_text):
            
            # Ganti command /<key> menjadi isi template
            def replacer(match):
                command = match.group(1).lower()
                return TEMPLATES.get(command, match.group(0))

            new_text = re.sub(PATTERN, replacer, original_text)

            # Eksekusi edit pesan secara instan!
            if new_text != original_text:
                await event.edit(new_text)
                
    except Exception as e:
        print(f"[❌ ERROR] Gagal mengedit pesan: {e}")

# ==========================================
# 3. RUNNER
# ==========================================
async def main():
    print("⏳ Menghidupkan Mode Auto-Replace Ubot...\n")
    try:
        await ubot.start()
        print("🚀 SISTEM AKTIF! Coba ketik '5k /a' atau '/s mantap' di chat mana pun.")
        await ubot.run_until_disconnected()
    except Exception as e:
        print(f"[❌ FATAL] Gagal nyala: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[🛑] Dihentikan user.")
