# -*- coding: utf-8 -*-
import telebot
import threading
import os
import io
import re
import zipfile
from flask import Flask, request, jsonify

# ==========================================
# 1. الإعدادات الأساسية
# ==========================================
TOKEN = '8617254929:AAGtY99XlCktp62gdPkWz7aNonDuvrLWjZc'
DASHBOARD_URL = "https://abdo-ai.onrender.com/" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_data = {}

# ==========================================
# 2. كلاس محرك التشفير (Signature & Bypass)
# ==========================================
class EncryptionModule:
    @staticmethod
    def extract_3d_signature(sig_bytes):
        """يستخرج بصمة الـ 3D من ملف CodeSignature"""
        match = re.search(rb'.{10,64}\x33\x44', sig_bytes)
        return match.group() if match else sig_bytes[:64]

    @staticmethod
    def apply_bypass(mod_bytes, sig_data, header):
        """حقن التشفير ومنع برامج Asset Bundle من الفتح"""
        magic = b"UnityFS\x00\x00\x00\x00\x07"
        # بايتات تشويش لكسر برامج الاستخراج الخارجية
        obfuscation = b"\x00\xff\x00\xff" 
        return magic + sig_data + header + obfuscation + mod_bytes

# ==========================================
# 3. كلاس محرك IDA Pro (Analysis Only)
# ==========================================
class IDAModule:
    @staticmethod
    def run_unpack(data):
        report = ["--- [ IDA UNPACK REPORT ] ---"]
        if zipfile.is_zipfile(io.BytesIO(data)):
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                report.extend([f"File: {n}" for n in z.namelist()])
        return "\n".join(report)

    @staticmethod
    def get_general_offsets(data):
        offsets = re.findall(rb'\x00\x00[\x00-\xFF]{2,4}', data)
        unique = sorted(list(set(offsets)))
        return "\n".join([f"Offset: 0x{o.hex().upper()}" for o in unique[:1000]])

    @staticmethod
    def get_strong_offsets(data):
        patterns = [rb'\xFD\x7B\xBF\xA9', rb'\xFF\x43\x00\xD1', rb'\x08\x00\x80\x52']
        results = ["--- [ STRONG FUNCTIONS ] ---"]
        for p in patterns:
            for m in re.finditer(p, data):
                results.append(f"Strong At: {hex(m.start()).upper()}")
        return "\n".join(results)

# ==========================================
# 4. كلاس واجهات الأزرار (Keyboards)
# ==========================================
class InterfaceModule:
    @staticmethod
    def main_menu():
        m = telebot.types.InlineKeyboardMarkup(row_width=1)
        m.add(
            telebot.types.InlineKeyboardButton("🚀 تشفير Signature Bypass", callback_data="btn_crypt"),
            telebot.types.InlineKeyboardButton("🛠 IDA Pro Menu", callback_data="btn_ida"),
            telebot.types.InlineKeyboardButton("🌐 لوحة التحكم", url=DASHBOARD_URL)
        )
        return m

    @staticmethod
    def ida_menu():
        m = telebot.types.InlineKeyboardMarkup(row_width=1)
        m.add(
            telebot.types.InlineKeyboardButton("🔓 فك الملفات (Unpack)", callback_data="ida_unpack"),
            telebot.types.InlineKeyboardButton("📊 أوفستات عامة", callback_data="ida_general"),
            telebot.types.InlineKeyboardButton("💎 أوفستات قوية (Strong)", callback_data="ida_strong"),
            telebot.types.InlineKeyboardButton("⬅️ رجوع", callback_data="btn_main")
        )
        return m

# ==========================================
# 5. منطق معالجة الرسائل والملفات
# ==========================================
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "⚡️ **ABDO TOP1 Engine**\nالنظام مفصل ومنظم الآن لتسهيل التعديل.", 
                     reply_markup=InterfaceModule.main_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    chat_id = call.message.chat.id
    if call.data == "btn_crypt":
        user_data[chat_id] = {'mode': 'crypt', 'step': 'original'}
        bot.send_message(chat_id, "1️⃣ أرسل **الملف الأصلي**:")
    
    elif call.data == "btn_ida":
        bot.edit_message_text("🛠 اختر أداة تحليل IDA:", chat_id, call.message.message_id, 
                              reply_markup=InterfaceModule.ida_keyboard())
    
    elif call.data == "btn_main":
        bot.edit_message_text("⚡️ القائمة الرئيسية:", chat_id, call.message.message_id, 
                              reply_markup=InterfaceModule.main_menu())
    
    elif call.data.startswith("ida_"):
        user_data[chat_id] = {'mode': call.data}
        bot.send_message(chat_id, f"📥 أرسل الملف للتحليل عبر {call.data}:")

@bot.message_handler(content_types=['document'])
def process_files(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    
    state = user_data[chat_id]
    file_bytes = bot.download_file(bot.get_file(message.document.file_id).file_path)

    # --- [ كود زر التشفير ] ---
    if state.get('mode') == 'crypt':
        if state['step'] == 'original':
            state.update({'header': file_bytes[:32], 'step': 'sig'})
            bot.reply_to(message, "✅ استلمت الأصلي.\n2️⃣ أرسل الآن ملف **_CodeSignature**:")
        
        elif state['step'] == 'sig':
            state.update({'sig_data': EncryptionModule.extract_3d_signature(file_bytes), 'step': 'mod'})
            bot.reply_to(message, "✅ تم استخراج بصمة 3D.\n3️⃣ أرسل الآن **الملف المعدل** للتشفير النهائي:")
            
        elif state['step'] == 'mod':
            bot.reply_to(message, "⚙️ جاري التشفير والحماية...")
            final = EncryptionModule.apply_bypass(file_bytes, state['sig_data'], state['header'])
            out = io.BytesIO(final); out.name = f"Crypt_{message.document.file_name}"
            bot.send_document(chat_id, out, caption="✅ تم التشفير بنجاح (محمي من الاستخراج).")
            del user_data[chat_id]

    # --- [ كود زر IDA Pro ] ---
    elif "ida" in state.get('mode'):
        mode = state.get('mode')
        bot.reply_to(message, "⚙️ IDA Analysis in progress...")
        
        if "unpack" in mode: report = IDAModule.run_unpack(file_bytes)
        elif "general" in mode: report = IDAModule.get_general_offsets(file_bytes)
        else: report = IDAModule.get_strong_offsets(file_bytes)
        
        res_file = io.BytesIO(report.encode()); res_file.name = f"{mode}_report.txt"
        bot.send_document(chat_id, res_file, caption=f"✅ اكتمل تحليل {mode}")
        del user_data[chat_id]

# ==========================================
# 6. تشغيل السيرفر والبوت
# ==========================================
@app.route('/')
def home(): return "Abdo-AI Organized Server LIVE 🚀"

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    bot.infinity_polling()
