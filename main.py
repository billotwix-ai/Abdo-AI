# -*- coding: utf-8 -*-
import telebot
import threading
import os
import io
import re
import zipfile
from flask import Flask, request, jsonify

# --- [ الإعدادات الأساسية ] ---
TOKEN = '8617254929:AAGtY99XlCktp62gdPkWz7aNonDuvrLWjZc'
DASHBOARD_URL = "https://abdo-ai.onrender.com/" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_data = {}

# --- [ محرك التشفير المتقدم - Free Fire Signature Bypass ] ---
class AbdoSecurityEngine:
    @staticmethod
    def extract_signature_values(sig_bytes):
        # استخراج البصمات والقيم الحساسة من ملف _CodeSignature
        # نبحث عن أنماط معينة تنتهي بـ 3D أو قيم التشفير الخاصة باللعبة
        signatures = re.findall(rb'[\x00-\xFF]{16,64}\x33\x44', sig_bytes)
        if signatures:
            return signatures[0]
        return sig_bytes[:128] # قيمة احتياطية

    @staticmethod
    def advanced_crypt(mod_bytes, sig_data, original_header):
        # نظام التشفير "الغامض":
        # 1. نضع توقيع UnityFS الصحيح للتمويه
        # 2. نحقن البصمة المستخرجة من CodeSignature
        # 3. ندمج الهيدر الأصلي
        # 4. نقوم بتغيير بسيط في هيكلية البايتات لمنع برامج Asset Bundle من قراءته
        
        magic = b"UnityFS\x00\x00\x00\x00\x07"
        # حماية إضافية: إضافة "بايتات تشويش" تمنع Asset Studio من التعرف على الملف
        obfuscation = b"\xff\xee\xaa\xbb" 
        
        return magic + sig_data + original_header + obfuscation + mod_bytes

# --- [ محرك IDA Pro التحليلي ] ---
class IDAProAdvanced:
    @staticmethod
    def extract_all(file_bytes):
        offsets = re.findall(rb'\x00\x00[\x00-\xFF]{2,4}', file_bytes)
        unique = sorted(list(set(offsets)))
        return [f"[ADDR] -> 0x{o.hex().upper()}" for o in unique[:1000]]

    @staticmethod
    def extract_strong(file_bytes):
        strong_patterns = [rb'\xFD\x7B\xBF\xA9', rb'\xFF\x43\x00\xD1', rb'\x08\x00\x80\x52']
        results = []
        for p in strong_patterns:
            for match in re.finditer(p, file_bytes):
                addr = hex(match.start()).upper()
                results.append(f"[STRONG] -> {addr}")
        return results[:500]

# --- [ سيرفر الويب ] ---
@app.route('/')
def home(): return "Abdo-AI Security Server is LIVE 🚀"

@app.route('/verify_now', methods=['GET', 'POST'])
def verify_now(): return jsonify({"status": "verified"})

# --- [ واجهات الأزرار ] ---
def main_keyboard():
    m = telebot.types.InlineKeyboardMarkup(row_width=1)
    m.add(
        telebot.types.InlineKeyboardButton("🚀 تشفير Bypass (Signature Mode)", callback_data="start_crypt"),
        telebot.types.InlineKeyboardButton("🛠 IDA Pro Menu", callback_data="ida_menu"),
        telebot.types.InlineKeyboardButton("🌐 لوحة التحكم", url=DASHBOARD_URL)
    )
    return m

def ida_keyboard():
    m = telebot.types.InlineKeyboardMarkup(row_width=1)
    m.add(
        telebot.types.InlineKeyboardButton("🔓 Unpack", callback_data="ida_unpack"),
        telebot.types.InlineKeyboardButton("📊 General Offsets", callback_data="ida_general"),
        telebot.types.InlineKeyboardButton("💎 Strong Offsets", callback_data="ida_strong"),
        telebot.types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_main")
    )
    return m

# --- [ معالجة الأوامر ] ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "⚡️ **نظام ABDO TOP1 الأمني**\nجاهز لتشفير فري فاير وتحليل IDA.", 
                     reply_markup=main_keyboard(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    chat_id = call.message.chat.id
    if call.data == "start_crypt":
        user_data[chat_id] = {'mode': 'crypt', 'step': 'original'}
        bot.send_message(chat_id, "1️⃣ أرسل **الملف الأصلي** الآن:")
    
    elif call.data == "ida_menu":
        bot.edit_message_text("🛠 خصائص تحليل IDA Pro:", chat_id, call.message.message_id, reply_markup=ida_keyboard())
    
    elif call.data.startswith("ida_"):
        user_data[chat_id] = {'mode': call.data}
        bot.send_message(chat_id, "📥 أرسل الملف للتحليل:")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    state = user_data[chat_id]
    downloaded = bot.download_file(bot.get_file(message.document.file_id).file_path)

    # --- [ مسار التشفير الثلاثي ] ---
    if state.get('mode') == 'crypt':
        if state['step'] == 'original':
            state['header'] = downloaded[:32]
            state['step'] = 'sig'
            user_data[chat_id] = state
            bot.reply_to(message, "✅ تم استلام الأصلي.\n2️⃣ أرسل الآن ملف **_CodeSignature** لاستخراج القيم:")
        
        elif state['step'] == 'sig':
            state['sig_data'] = AbdoSecurityEngine.extract_signature_values(downloaded)
            state['step'] = 'mod'
            user_data[chat_id] = state
            bot.reply_to(message, "✅ تم استخراج بصمة الـ 3D.\n3️⃣ أرسل الآن **الملف المعدل** للتشفير ومنع أدوات الاستخراج:")
            
        elif state['step'] == 'mod':
            bot.reply_to(message, "⚙️ جاري التشفير بنظام حماية Abdo-AI...")
            final = AbdoSecurityEngine.advanced_crypt(downloaded, state['sig_data'], state['header'])
            out = io.BytesIO(final); out.name = f"Encrypted_{message.document.file_name}"
            bot.send_document(chat_id, out, caption="✅ **تم التشفير بنجاح!**\n- صالح للعبة فري فاير.\n- محمي من برامج Assets Bundle.")
            del user_data[chat_id]

    # --- [ مسار IDA Pro ] ---
    elif "ida" in state.get('mode'):
        mode = state.get('mode')
        report = IDAProAdvanced.extract_all(downloaded) if "general" in mode else IDAProAdvanced.extract_strong(downloaded)
        res_name = f"IDA_{mode}.txt"
        with open(res_name, "w") as f: f.write("\n".join(report))
        with open(res_name, "rb") as f: bot.send_document(chat_id, f, caption="✅ تقرير IDA جاهز.")
        os.remove(res_name); del user_data[chat_id]

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    bot.infinity_polling()
