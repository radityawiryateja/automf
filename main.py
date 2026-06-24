import asyncio
import os
import re
import itertools
import logging
import html
import aiohttp
from datetime import datetime, timezone
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateStatusRequest

# ==========================================
# 1. KONFIGURASI & INIT
# ==========================================
logging.getLogger('telethon').setLevel(logging.ERROR)
load_dotenv()

try:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID"))
    
    raw_admin_ids = os.getenv("ADMIN_IDS", "")
    ADMINS = [int(os.getenv("OWNER_ID"))]
    if raw_admin_ids:
        ADMINS.extend([int(x.strip()) for x in raw_admin_ids.split(",") if x.strip()])

    raw_channels = os.getenv("TARGET_CHANNELS", "").split(",")
    TARGET_CHANNELS = []
    for ch in raw_channels:
        ch = ch.strip()
        if ch.startswith('-') or ch.isdigit():
            TARGET_CHANNELS.append(int(ch))
        elif ch:
            TARGET_CHANNELS.append(ch)

except Exception as e:
    print(f"[❌ FATAL ERROR] Gagal memuat konfigurasi .env: {e}")
    exit(1)

KEYWORDS = ["teleprem", "star", "mb", "moodboard", "manip", "wd", "wording", "fmv", "tgprem", "nokos", "noktel", "nokwa", "gift", "scribble", "icon", "bio", "bundle", "robux"]

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

ubot1 = TelegramClient(StringSession(os.getenv("UBOT1_SESSION")), API_ID, API_HASH, **CLIENT_PARAMS)
ubot2 = TelegramClient(StringSession(os.getenv("UBOT2_SESSION")), API_ID, API_HASH, **CLIENT_PARAMS)

BOT_TOKENS = [os.getenv("BOT_TOKEN_1"), os.getenv("BOT_TOKEN_2")]
bot_cycle = itertools.cycle(BOT_TOKENS)

# Jalur Tol Permanen HTTP
http_session = None


# ==========================================
# 2. FITUR BACKGROUND: ALWAYS ONLINE
# ==========================================
async def keep_always_online():
    print("🟢 Pengaktif status 'Online' berjalan di background...")
    while True:
        try:
            await ubot1(UpdateStatusRequest(offline=False))
            await ubot2(UpdateStatusRequest(offline=False))
        except Exception:
            pass
        await asyncio.sleep(300) # Update tiap 5 menit


# ==========================================
# 3. FASE DETEKSI & JALUR API INSTAN
# ==========================================
@ubot1.on(events.NewMessage(chats=TARGET_CHANNELS))
async def detection_handler(event):
    try:
        # [NEW] Auto-Read biar bubble di HP bersih!
        await ubot1.send_read_acknowledge(event.chat_id, event.message.id)

        if not event.message.text:
            return
            
        text = event.message.text.lower()
        
        if any(kw in text for kw in KEYWORDS):
            msg_id = event.message.id
            exact_chat_id = event.chat_id
            
            # CEK SELISIH WAKTU (DELAY JARINGAN)
            msg_time = event.message.date 
            now_time = datetime.now(timezone.utc)
            selisih_detik = (now_time - msg_time).total_seconds()
            tanda_delay = f" ⚠️ (Telat {int(selisih_detik)}d dari server)" if selisih_detik > 5 else ""
            
            chat_str = str(exact_chat_id).replace('-100', '') if str(exact_chat_id).startswith('-100') else str(exact_chat_id)
            msg_link = f"https://t.me/c/{chat_str}/{msg_id}"
            
            safe_text = html.escape(text[:150])
            notification_text = (
                f"🚨 <b>Menfess Terdeteksi!</b>{tanda_delay}\n\n"
                f"<b>Pesan:</b> {safe_text}...\n"
                f"🔗 <b>Link:</b> <a href='{msg_link}'>Cek Kesini</a>\n\n"
                f"💬 <i>Balas pesan ini dengan command</i>\n\n"
                f"<code>REF:{exact_chat_id}:{msg_id}</code>" 
            )
            
            current_token = next(bot_cycle)
            
            async def send_notif_http(token, text_payload, chat_target):
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                payload = {
                    "chat_id": ADMIN_GROUP_ID,
                    "text": text_payload,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                }
                try:
                    async with http_session.post(url, json=payload) as resp:
                        waktu = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        if resp.status == 200:
                            print(f"[{waktu}] ⚡ [API] Target {chat_target} | Delay: {int(selisih_detik)}s", flush=True)
                        else:
                            print(f"[{waktu}] [❌ ERROR API] Response: {await resp.text()}", flush=True)
                except Exception as e:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [❌ ERROR JARINGAN] API: {e}", flush=True)

            asyncio.create_task(send_notif_http(current_token, notification_text, exact_chat_id))
            
    except Exception as e:
        print(f"[❌ ERROR DETEKSI] {e}", flush=True)


# ==========================================
# 4. FASE EKSEKUSI (UBOT 2)
# ==========================================
@ubot2.on(events.NewMessage(chats=ADMIN_GROUP_ID, pattern=r'^/(\w+)'))
async def command_handler(event):
    try:
        if event.sender_id not in ADMINS:
            return 
        if not event.is_reply:
            return

        command = event.pattern_match.group(1).lower()
        if command not in TEMPLATES:
            return

        replied_msg = await event.get_reply_message()
        if not replied_msg or not replied_msg.text:
            return
            
        ref_match = re.search(r'`REF:(-?\d+):(\d+)`', replied_msg.text)
        if not ref_match:
            return

        target_chat = int(ref_match.group(1))
        target_msg_id = int(ref_match.group(2))
        wording = TEMPLATES[command]

        waktu_eksekusi = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{waktu_eksekusi}] [⏳] Ubot 2 otw komen ke {target_chat}...", flush=True)
        
        await ubot2.send_message(
            entity=target_chat,
            message=wording,
            comment_to=target_msg_id
        )
        
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [✅] Komentar sukses!", flush=True)
        
        try:
            await event.client.send_reaction(event.chat_id, event.message.id, '👍')
        except:
            pass 
            
    except Exception as e:
        print(f"[❌ ERROR EKSEKUSI] {e}", flush=True)


# ==========================================
# 5. RUNNER
# ==========================================
async def main_loop():
    global http_session
    
    print("⏳ Menghidupkan Mesin Ubot...\n")
    
    http_session = aiohttp.ClientSession()
    
    try:
        print("-> Starting Ubot 1 (Detector)...")
        await ubot1.start()
    except Exception as e:
        print(f"[❌ ERROR] Ubot 1 gagal: {e}")
        
    try:
        print("-> Starting Ubot 2 (Executor)...")
        await ubot2.start()
    except Exception as e:
        print(f"[❌ ERROR] Ubot 2 gagal: {e}")

    print("\n🚀 SISTEM ONLINE! (Mode API Super Kencang Aktif)\n")
    
    # Jalankan Keep Online di background
    asyncio.create_task(keep_always_online())

    try:
        await asyncio.gather(
            ubot1.run_until_disconnected(),
            ubot2.run_until_disconnected()
        )
    finally:
        await http_session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\n[🛑] Dihentikan user.")
