import requests, os, psutil, sys, jwt, pickle, json, binascii, time, urllib3, xKEys, base64, datetime, re, socket, threading, http.client, ssl, gzip, asyncio, gc, random, signal
from io import BytesIO
from protobuf_decoder.protobuf_decoder import Parser
from zakofadai import *  # تم تغيير الاسم
from datetime import datetime, timedelta
from google.protobuf.timestamp_pb2 import Timestamp
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from cfonts import render, say
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from telebot import TeleBot, types


console = Console()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BOT_TOKEN = "BOT_TOKEN"  # ضع توكن بوتك هنا
ADMIN_ID = ADMIN_ID # ضع معرفك هنا
bot = TeleBot(BOT_TOKEN)

MESSAGES = [
    "[b][c]ZAKARIA",
    "[b][c]ZikoB0SS",
    "[b][c]ZAKO HERE",
    "[b][c]KING ZAKARIA",
    "[b][c]ZIKO ON TOP",
    "[b][c]TEAM ZAKARIA",
    "[b][c]GLOBAL SPAMMER",
    "[b][c]ZAKO BOT",
    "[b][c]FF ZAKARIA",
    "[b][c]ZIKO SPAM",
    "[b][c]ZAKARIA KING",
    "[b][c]ZIKO BOSS",
    "[b][c]ZAKO GLOBAL",
    "[b][c]TEAM ZIKO",
    "[b][c]ZAKARIA FF",
]

bots_status = {}
bots_count = 0
total_messages_sent = 0
start_time = time.time()
active_bot_clients = []
shutdown_event = threading.Event()

class TelegramBotManager:
    def __init__(self):
        self.running = True
        self.setup_commands()
    
    def setup_commands(self):
        @bot.message_handler(commands=['start'])
        def start_command(message):
            if message.chat.id == ADMIN_ID:
                self.send_admin_panel()
        
        @bot.message_handler(commands=['status'])
        def status_command(message):
            if message.chat.id == ADMIN_ID:
                self.send_status()
        
        @bot.message_handler(commands=['add'])
        def add_command(message):
            if message.chat.id == ADMIN_ID:
                msg = bot.send_message(message.chat.id, "أرسل الحسابات بصيغة:\nuid:password\nuid2:password2")
                bot.register_next_step_handler(msg, self.process_add_accounts)
        
        @bot.message_handler(commands=['stop'])
        def stop_command(message):
            if message.chat.id == ADMIN_ID:
                self.stop_all_bots()
        
        @bot.message_handler(commands=['restart'])
        def restart_command(message):
            if message.chat.id == ADMIN_ID:
                self.restart_bots()
        
        @bot.message_handler(commands=['speed'])
        def speed_command(message):
            if message.chat.id == ADMIN_ID:
                self.change_speed()
        
        @bot.message_handler(commands=['message'])
        def message_command(message):
            if message.chat.id == ADMIN_ID:
                self.change_messages()
        
        @bot.message_handler(commands=['clear'])
        def clear_command(message):
            if message.chat.id == ADMIN_ID:
                self.clear_accounts()
        
        @bot.message_handler(commands=['logs'])
        def logs_command(message):
            if message.chat.id == ADMIN_ID:
                self.send_logs()
        
        @bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            if call.message.chat.id == ADMIN_ID:
                self.handle_callback(call)
    
    def send_admin_panel(self):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("📊 الحالة", callback_data="status")
        btn2 = types.InlineKeyboardButton("➕ إضافة حسابات", callback_data="add")
        btn3 = types.InlineKeyboardButton("🛑 إيقاف البوتات", callback_data="stop")
        btn4 = types.InlineKeyboardButton("🔄 إعادة تشغيل", callback_data="restart")
        btn5 = types.InlineKeyboardButton("⚡ تغيير السرعة", callback_data="speed")
        btn6 = types.InlineKeyboardButton("✉️ تغيير الرسائل", callback_data="message")
        btn7 = types.InlineKeyboardButton("🗑️ حذف الحسابات", callback_data="clear")
        btn8 = types.InlineKeyboardButton("📋 السجلات", callback_data="logs")
        
        markup.add(btn1, btn2)
        markup.add(btn3, btn4)
        markup.add(btn5, btn6)
        markup.add(btn7, btn8)
        
        bot.send_message(ADMIN_ID, "🤖 ZAKARIA SPAMMER BOT", reply_markup=markup)
    
    def send_status(self):
        global bots_count, total_messages_sent, start_time
        uptime = str(timedelta(seconds=int(time.time() - start_time)))
        active_bots = sum(1 for status in bots_status.values() if status == "online")
        
        status_text = f"""
╔════════════════════╗
   🤖  ZAKARIA BOT
╠════════════════════╣
 📊 عدد البوتات      » {bots_count}
 🟢 النشطة           » {active_bots}
 ✉️ الرسائل          » {total_messages_sent}
 ⏳ وقت التشغيل      » {uptime}
 🔌 الخدمة           » {"🟢 نشطة" if self.running else "🔴 متوقفة"}
╚════════════════════╝
        """
        
        bot.send_message(ADMIN_ID, status_text, parse_mode="Markdown")
    
    def process_add_accounts(self, message):
        try:
            lines = message.text.split('\n')
            new_accounts = {}
            
            for line in lines:
                if ':' in line:
                    uid, pwd = line.strip().split(':', 1)
                    new_accounts[uid] = pwd
            
            if os.path.exists("accs.json"):
                with open("accs.json", "r") as f:
                    accounts = json.load(f)
            else:
                accounts = {}
            
            accounts.update(new_accounts)
            
            with open("accs.json", "w") as f:
                json.dump(accounts, f)
            
            bot.send_message(ADMIN_ID, f"✅ تم إضافة {len(new_accounts)} حساب بنجاح")
            
            for uid, pwd in new_accounts.items():
                client = FF_CLient(uid, pwd)
                
                if hasattr(client, 'ip') and client.ip:
                    active_bot_clients.append(client)
                    t = Thread(target=client.start)
                    t.daemon = True
                    t.start()
                
        except Exception as e:
            bot.send_message(ADMIN_ID, f"❌ خطأ: {str(e)}")
    
    def stop_all_bots(self):
        global shutdown_event
        self.running = False
        shutdown_event.set()
        
        for client in active_bot_clients:
            client.stop()
        
        bot.send_message(ADMIN_ID, "✅ تم إيقاف جميع البوتات بنجاح")
    
    def restart_bots(self):
        self.running = True
        bot.send_message(ADMIN_ID, "🔄 جاري إعادة تشغيل البوتات...")
        os.execv(sys.executable, ['python'] + sys.argv)
    
    def change_speed(self):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("🐢 بطيء", callback_data="speed_slow")
        btn2 = types.InlineKeyboardButton("⚡ عادي", callback_data="speed_normal")
        btn3 = types.InlineKeyboardButton("🚀 سريع", callback_data="speed_fast")
        markup.add(btn1, btn2, btn3)
        bot.send_message(ADMIN_ID, "اختر السرعة:", reply_markup=markup)
    
    def change_messages(self):
        bot.send_message(ADMIN_ID, "أرسل الرسائل الجديدة (كل رسالة في سطر)")
    
    def clear_accounts(self):
        if os.path.exists("accs.json"):
            os.remove("accs.json")
        bot.send_message(ADMIN_ID, "✅ تم حذف جميع الحسابات")
    
    def send_logs(self):
        try:
            with open("bot_logs.txt", "r") as f:
                lines = f.readlines()[-50:]
            bot.send_message(ADMIN_ID, "📋 **آخر 50 سطر من السجلات:**\n" + "".join(lines))
        except:
            bot.send_message(ADMIN_ID, "لا توجد سجلات حالياً")
    
    def handle_callback(self, call):
        if call.data == "status":
            self.send_status()
        elif call.data == "add":
            self.add_command(call.message)
        elif call.data == "stop":
            self.stop_all_bots()
        elif call.data == "restart":
            self.restart_bots()
        elif call.data in ["speed_slow", "speed_normal", "speed_fast"]:
            speed_text = {"speed_slow": "بطيء 🐢", "speed_normal": "عادي ⚡", "speed_fast": "سريع 🚀"}[call.data]
            bot.send_message(ADMIN_ID, f"✅ تم تغيير السرعة إلى {speed_text}")
        elif call.data == "message":
            self.change_messages()
        elif call.data == "clear":
            self.clear_accounts()
        elif call.data == "logs":
            self.send_logs()
        
        bot.answer_callback_query(call.id)
    
    def start_telegram_bot(self):
        while not shutdown_event.is_set():
            try:
                bot.polling(none_stop=True, timeout=30, long_polling_timeout=20)
            except Exception as e:
                print(f"Telegram bot error: {e}")
                time.sleep(5)

def G_AccEss(U, P):
    UrL = "https://100067.connect.garena.com/oauth/guest/token/grant"
    HE = {"Host": "100067.connect.garena.com", "User-Agent": Ua(), "Content-Type": "application/x-www-form-urlencoded", "Accept-Encoding": "gzip, deflate, br", "Connection": "close"}
    dT = {"uid": f"{U}", "password": f"{P}", "response_type": "token", "client_type": "2", "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3", "client_id": "100067"}
    try:
        R = requests.post(UrL, headers=HE, data=dT)
        if R.status_code == 200: 
            return R.json()['access_token'], R.json()['open_id']
        else: 
            print(R.json())
    except Exception as e: 
        print(e)
        ResTarTinG()
    return None, None 

def MajorLoGin(PyL):
    context = ssl._create_unverified_context()
    conn = http.client.HTTPSConnection("loginbp.ggpolarbear.com", context=context)
    headers = {
        'X-Unity-Version': '2018.4.11f1', 
        'ReleaseVersion': 'OB52',
        'Content-Type': 'application/x-www-form-urlencoded', 
        'X-GA': 'v1 1',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; ar_SA; SM-G973F Build/PPR1.180610.011)',
        'Host': 'loginbp.ggpolarbear.com', 
        'Connection': 'Keep-Alive', 
        'Accept-Encoding': 'gzip'
    }
    try:
        conn.request("POST", "/MajorLogin", body=PyL, headers=headers)
        response = conn.getresponse()
        raw_data = response.read()
        if response.getheader('Content-Encoding') == 'gzip':
            with gzip.GzipFile(fileobj=BytesIO(raw_data)) as f:
                raw_data = f.read()
        TexT = raw_data.decode(errors='ignore')
        if 'BR_PLATFORM_INVALID_OPENID' in TexT or 'BR_GOP_TOKEN_AUTH_FAILED' in TexT: 
            sys.exit()
        return raw_data.hex() if response.status in [200, 201] else None
    finally: 
        conn.close()

Thread(target=AuTo_ResTartinG, daemon=True).start()

class FF_CLient:
    def __init__(self, U, P):
        self.uid = U
        self.pwd = P
        self.reader = None
        self.writer = None
        self.reader2 = None
        self.writer2 = None
        self.loop = None
        self._stop_event = asyncio.Event()
        
        global bots_count
        bots_count += 1
        bots_status[U] = "initializing"
        
        token_data = self.ToKen_GeneRaTe(U, P)
        
        if not token_data:
            print(f"❌ فشل تسجيل الدخول للحساب {U}. سيتم تجاهله.")
            bots_status[U] = "login_failed"
            return
        
        try:
            self.JwT_ToKen, self.key, self.iv, self.combined_timestamp, self.ip, self.port, self.ip2, self.port2, self.bot_uid = token_data
        except (ValueError, TypeError) as e:
            print(f"❌ خطأ في بيانات التوكن للحساب {U}: {e}. سيتم تجاهله.")
            bots_status[U] = "data_error"
            return
        
        self.AutH_ToKen = self.Get_FiNal_ToKen_0115()
        if not self.AutH_ToKen:
            print(f"❌ فشل إنشاء التوكن النهائي للحساب {U}. سيتم تجاهله.")
            bots_status[U] = "final_token_failed"
            return

    def start(self):
        if not hasattr(self, 'ip') or not self.ip:
            print(f"Skipping start for bot {self.uid} due to failed initialization.")
            return
        asyncio.run(self._run_async_tasks())

    async def _run_async_tasks(self):
        self.loop = asyncio.get_running_loop()
        try:
            await self.STarT()
        except asyncio.CancelledError:
            print(f"Bot {self.uid} tasks cancelled.")
        except Exception as e:
            print(f"Bot {self.uid} encountered an error: {e}")
            bots_status[self.uid] = "error"
        finally:
            await self._cleanup_resources()

    def stop(self):
        if self.loop:
            self.loop.call_soon_threadsafe(self._stop_event.set)

    async def _cleanup_resources(self):
        print(f"Cleaning up resources for bot {self.uid}")
        if self.writer:
            try: 
                self.writer.close()
                await self.writer.wait_closed()
            except Exception: 
                pass
        if self.writer2:
            try: 
                self.writer2.close()
                await self.writer2.wait_closed()
            except Exception: 
                pass
        self.reader, self.writer, self.reader2, self.writer2 = None, None, None, None
        gc.collect()

    async def STarT(self):
        try:
            chat_task = asyncio.create_task(self.ChaT())
            online_task = asyncio.create_task(self.OnLinE())
            
            await asyncio.gather(chat_task, online_task, return_exceptions=True)
        except Exception as e:
            print(f"Error in STarT for bot {self.uid}: {e}")

    async def OnLinE(self):
        while not self._stop_event.is_set():
            try:
                self.reader2, self.writer2 = await asyncio.wait_for(asyncio.open_connection(self.ip2, int(self.port2)), timeout=10)
                await self.writer2.drain()
                self.writer2.write(bytes.fromhex(self.AutH_ToKen))
                await self.writer2.drain()
                
                bots_status[self.uid] = "online"
                while not self._stop_event.is_set():
                    try:
                        self.DaTa = await asyncio.wait_for(self.reader2.read(9999), timeout=10)
                        if not self.DaTa: 
                            break
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        break
            except (asyncio.TimeoutError, ConnectionRefusedError, ConnectionResetError, OSError) as e:
                bots_status[self.uid] = "reconnecting"
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Unexpected error in OnLinE for bot {self.uid}: {e}")
                await asyncio.sleep(5)
        bots_status[self.uid] = "offline"

    async def ChaT(self):
        T = 'ar'
        while not self._stop_event.is_set():
            try:
                self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(self.ip, int(self.port)), timeout=10)
                self.writer.write(bytes.fromhex(self.AutH_ToKen))
                await self.writer.drain()
                await asyncio.sleep(0.5)
                self.writer.write(ZAKO_GLobaL(T, self.key, self.iv))
                await self.writer.drain()
                await asyncio.sleep(0.5)
                
                while not self._stop_event.is_set():
                    try:
                        self.DaTa = await asyncio.wait_for(self.reader.read(9999), timeout=10)
                        if not self.DaTa: 
                            break
                        
                        if self.DaTa.hex().startswith("1200") and b"SecretCode" in self.DaTa:
                            U = json.loads(DeCode_PackEt(self.DaTa.hex()[10:]))
                            U2 = json.loads(DeCode_PackEt(self.DaTa.hex()[36:]))
                            Uu = json.loads(U["5"]["data"]["8"]["data"])
                            
                            TarGeT = int(Uu['GroupID'])
                            sQ = Uu['SecretCode']
                            
                            message = random.choice(MESSAGES)
                            
                            self.writer.write(ZAKO_3alamyia_Chat(TarGeT, sQ, self.key, self.iv))
                            await self.writer.drain()
                            self.writer.write(ZAKO_SendMsg(f"[[iِ][bِ][cِ][FFFFFF][B][B][B][B][B][C]{xMsGFixinG(message)}", TarGeT, self.bot_uid, self.key, self.iv))
                            await self.writer.drain()
                            
                            await asyncio.sleep(1)
                            
                            if self.writer2 and not self.writer2.is_closing():
                                self.writer2.write(ZAKO_SendInv(self.bot_uid, TarGeT, self.key, self.iv))
                                await self.writer2.drain()
                            
                            self.writer2.write(Join_Sq(T, TarGeT, sQ, self.key, self.iv))
                            await self.writer2.drain()
                            
                            self.writer.write(quit_caht_zako(TarGeT, self.key, self.iv))
                            await self.writer.drain()
                            
                            global total_messages_sent
                            total_messages_sent += 1
                            
                            with open("bot_logs.txt", "a", encoding='utf-8') as f:
                                f.write(f"{datetime.now()} - Bot {self.bot_uid} sent message to room {TarGeT}\n")
                            
                            print(f"✅ ZAKARIA => {self.bot_uid} إلى => {TarGeT}")
                            await asyncio.sleep(3)

                    except asyncio.TimeoutError:
                        continue
                    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                        break
                    except Exception as e:
                        print(f"Error in chat loop for bot {self.uid}: {e}")
                        break
                        
            except (asyncio.TimeoutError, ConnectionRefusedError, ConnectionResetError, OSError) as e:
                bots_status[self.uid] = "reconnecting"
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Unexpected error in ChaT for bot {self.uid}: {e}")
                await asyncio.sleep(5)
        bots_status[self.uid] = "offline"

    def GeT_Key_Iv(self, serialized_data):
        my_message = xKEys.MyMessage()
        my_message.ParseFromString(serialized_data)
        timestamp = my_message.field21
        key = my_message.field22
        iv = my_message.field23
        
        timestamp_obj = Timestamp()
        timestamp_obj.FromNanoseconds(timestamp)
        timestamp_seconds = timestamp_obj.seconds
        timestamp_nanos = timestamp_obj.nanos
        combined_timestamp = timestamp_seconds * 1_000_000_000 + timestamp_nanos
        
        return combined_timestamp, key, iv

    def GeT_LoGin_PorTs(self, JwT_ToKen, PayLoad):
        self.UrL = 'https://clientbp.ggpolarbear.com/GetLoginData'
        self.HeadErs = {
            'Expect': '100-continue', 
            'Authorization': f'Bearer {JwT_ToKen}',
            'X-Unity-Version': '2018.4.11f1', 
            'X-GA': 'v1 1', 
            'ReleaseVersion': 'OB52',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; ar_SA; SM-G973F Build/PPR1.180610.011)',
            'Host': 'clientbp.ggpolarbear.com', 
            'Connection': 'close', 
            'Accept-Encoding': 'gzip, deflate, br'
        }
        try:
            self.Res = requests.post(self.UrL, headers=self.HeadErs, data=PayLoad, verify=False)
            self.BesTo_data = json.loads(DeCode_PackEt(self.Res.content.hex()))
            address = self.BesTo_data['32']['data']
            address2 = self.BesTo_data['14']['data']
            
            ip = address[:len(address) - 6]
            ip2 = address2[:len(address2) - 6]
            port = address[len(address) - 5:]
            port2 = address2[len(address2) - 5:]
            
            return ip, port, ip2, port2
        except requests.RequestException as e:
            print(f" - Bad Requests for UID {self.uid}!")
        except Exception as e:
            print(f" - Failed To GeT PorTs for UID {self.uid}: {e}")
        return None, None, None, None

    def ToKen_GeneRaTe(self, U, P):
        try:
            if U and P:
                self.PLaFTrom = 4
                self.A, self.O = G_AccEss(U, P)
                if not self.A or not self.O: 
                    print(f"G_AccEss failed for UID {self.uid}")
                    return None

                self.Version = '2019118695'
                self.V = '1.120.1'
                
                self.PyL = {
                    3: str(datetime.now())[:-7], 
                    4: "free fire", 
                    5: 1, 
                    7: self.V,
                    8: "Android OS 11 / API-30 (R/RQ3A.211001.001) ar_SA", 
                    9: "Handheld",
                    10: "Zain SA", 
                    11: "WIFI", 
                    12: 1440, 
                    13: 3200, 
                    14: "420",
                    15: "Exynos 990 (E1080) | 2800 | 8", 
                    16: 5951, 
                    17: "Mali-G77 MP11",
                    18: "OpenGL ES 3.2", 
                    19: "Samsung|e2b9e8e5-c844-4e8a-b4f9-3e4c7b3d2a1f",
                    20: "188.121.40.76", 
                    21: "ar_SA", 
                    22: self.O, 
                    23: self.PLaFTrom,
                    24: "Handheld", 
                    25: "samsung SM-G973F", 
                    29: self.A, 
                    30: 1,
                    41: "Zain SA", 
                    42: "WIFI", 
                    57: "1ac4b80ecf0478a44203bf8fac6120f5",
                    60: 32966, 
                    61: 29779, 
                    62: 2479, 
                    63: 914, 
                    64: 31176, 
                    65: 32966,
                    66: 31176, 
                    67: 32966, 
                    70: 4, 
                    73: 2,
                    74: "/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/lib/arm64",
                    76: 1, 
                    77: "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/base.apk",
                    78: 6, 
                    79: 1, 
                    81: "64", 
                    83: self.Version, 
                    86: "OpenGLES3",
                    87: 255, 
                    88: self.PLaFTrom,
                    89: "J\u0003FD\u0004\r_UH\u0003\u000b\u0016_\u0003D^J>\u000fWT\u0000\\=\nQ_;\u0000\r;Z\u0005a",
                    90: "Riyadh", 
                    91: "SA", 
                    92: 10214, 
                    93: "3rd_party",
                    94: "KqsHT7gtKWkK0gY/HwmdwXIhSiz4fQldX3YjZeK86XBTthKAf1bW4Vsz6Di0S8vqr0Jc4HX3TMQ8KaUU3GeVvYzWF9I=",
                    95: 111207, 
                    97: 1, 
                    98: 1, 
                    99: f"{self.PLaFTrom}", 
                    100: f"{self.PLaFTrom}"
                }
                
                try:
                    self.PyL_hex = CrEaTe_ProTo(self.PyL).hex()
                    self.PaYload = bytes.fromhex(EnC_AEs(self.PyL_hex))
                except Exception as e:
                    print(f"Proto/AES error for UID {self.uid}: {e}")
                    return None
                    
                self.ResPonse = MajorLoGin(self.PaYload)
                if self.ResPonse:
                    self.BesTo_data = json.loads(DeCode_PackEt(self.ResPonse))
                    self.bot_uid = self.BesTo_data['1']['data']
                    self.JwT_ToKen = self.BesTo_data['8']['data']
                    self.combined_timestamp, self.key, self.iv = self.GeT_Key_Iv(bytes.fromhex(self.ResPonse))
                    
                    ip, port, ip2, port2 = self.GeT_LoGin_PorTs(self.JwT_ToKen, self.PaYload)
                    if ip and port and ip2 and port2:
                        return self.JwT_ToKen, self.key, self.iv, self.combined_timestamp, ip, port, ip2, port2, self.bot_uid
                    else:
                        print(f"Failed to get ports for UID {self.uid}")
                        return None
                else:
                    print(f"MajorLoGin failed for UID {self.uid}")
                    return None
        except Exception as e:
            print(f'Exception in ToKen_GeneRaTe for UID {self.uid}: {e}')
            return None

    def Get_FiNal_ToKen_0115(self):
        token = self.JwT_ToKen
        try:
            self.AfTer_DeC_JwT = jwt.decode(token, options={"verify_signature": False})
            self.AccounT_Uid = self.AfTer_DeC_JwT.get('account_id')
            self.Nm = self.AfTer_DeC_JwT.get('nickname')
            self.H, self.M, self.S = GeT_Time(self.AfTer_DeC_JwT.get('exp'))
            self.Vr = self.AfTer_DeC_JwT.get('release_version')
            self.EncoDed_AccounT = hex(self.AccounT_Uid)[2:]
            self.HeX_VaLue = DecodE_HeX(self.combined_timestamp)
            self.TimE_HEx = self.HeX_VaLue
            self.JwT_ToKen_ = token.encode().hex()
        except Exception as e:
            print(f" - Error In ToKen for UID {self.uid}: {e}")
            return None
            
        try:
            encrypted_token = EnC_PacKeT(self.JwT_ToKen_, self.key, self.iv)
            self.Header = hex(len(encrypted_token) // 2)[2:]
            
            length = len(self.EncoDed_AccounT)
            if length == 9: 
                padding = '0000000'
            elif length == 8: 
                padding = '00000000'
            elif length == 10: 
                padding = '000000'
            elif length == 7: 
                padding = '000000000'
            else:
                padding = '00000000'
                print('Unexpected length encountered')
                
            self.Header = f'0115{padding}{self.EncoDed_AccounT}{self.TimE_HEx}00000{self.Header}'
            self.FiNal_ToKen_0115 = self.Header + encrypted_token
        except Exception as e:
            print(f" - Error In Final Token for UID {self.uid}: {e}")
            return None
            
        return self.FiNal_ToKen_0115

def load_accounts(file_path="accs.json"):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print(f"File {file_path} does not exist.")
        return {}

def StarT_SerVer():
    print(render('ZAKARIA', colors=['white', 'yellow'], align='center'))
    TexT = f'[معلومات الهدف] > البوتات متصلة\n[حالة البوت] > [bold green]تم الاتصال بنجاح[/bold green]\n[تلجرام] > [bold blue]@ZikoB0SS[/bold blue]'
    panel = Panel(Align.center(TexT), title="[bold yellow]ZAKARIA - GLOBAL SPAMMER[/bold yellow]", border_style="bright_yellow", padding=(1, 2), expand=False)
    console.print(panel)
    
    # إنشاء ملف السجلات إذا لم يكن موجوداً
    if not os.path.exists("bot_logs.txt"):
        with open("bot_logs.txt", "w", encoding='utf-8') as f:
            f.write(f"{datetime.now()} - Bot started\n")
    
    try:
        bot.send_message(ADMIN_ID, "✅ تم بدء تشغيل بوت ZAKARIA بنجاح!")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
    
    accounts = load_accounts()
    print(f"Loaded {len(accounts)} accounts")
    
    for uid, pwd in accounts.items():
        client = FF_CLient(uid, pwd)
        if hasattr(client, 'ip') and client.ip:
            active_bot_clients.append(client)
            t = Thread(target=client.start)
            t.daemon = True
            t.start()
            time.sleep(0.1)

def signal_handler(sig, frame):
    print("\nShutdown signal received. Stopping bots...")
    shutdown_event.set()
    telegram_manager.stop_all_bots()
    sys.exit(0)

if __name__ == "__main__":
    # إنشاء ملف السجلات عند البدء
    if not os.path.exists("bot_logs.txt"):
        with open("bot_logs.txt", "w", encoding='utf-8') as f:
            f.write(f"{datetime.now()} - Bot started\n")
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    telegram_manager = TelegramBotManager()
    telegram_thread = Thread(target=telegram_manager.start_telegram_bot)
    telegram_thread.daemon = True
    telegram_thread.start()
    
    StarT_SerVer()
    
    try:
        while not shutdown_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)