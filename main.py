# -*- coding: utf-8 -*-
import telebot
import threading
import os
import io
import zipfile
import re
from flask import Flask, request, jsonify

# --- [ الإعدادات الأساسية ] ---
TOKEN = '8617254929:AAGtY99XlCktp62gdPkWz7aNonDuvrLWjZc'
DASHBOARD_URL = "https://abdo-ai.onrender.com/" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_data = {}

# --- [ محرك IDA Pro المتقدم ] ---
class IDAProAdvanced:
    @staticmethod
    def extract_all(file_bytes):
        offsets = re.findall(rb'\x00\x00[\x00-\xFF]{2,4}', file_bytes)
        unique = sorted(list(set(offsets)))
        return [f"[ADDR] -> 0x{o.hex().upper()}" for o in unique[:1000]]

    @staticmethod
    def extract_strong(file_bytes):
        strong_patterns = [
            rb'\xFD\x7B\xBF\xA9', # بداية الدالة
            rb'\xFF\x43\x00\xD1', # تخصيص الذاكرة
            rb'\x08\x00\x80\x52'  # قيم العودة المشهورة
        ]
        results = []
        for p in strong_patterns:
            for match in re.finditer(p, file_bytes):
                addr = hex(match.start()).upper()
                results.append(f"[STRONG_OFFSET] -> {addr} | Pattern: {p.hex().upper()}")
        return results[:500]

# --- [ محرك التشفير الخاص - Signature 3D Bypass ] ---
class AbdoBypassEngine:
    @staticmethod
    def extract_3d_signature(sig_bytes):
        # البحث عن نمط البصمة الذي ينتهي بـ 3D (Hex: 33 44)
        match = re.search(rb'.{10,64}\x33\x44', sig_bytes)
        if match:
            return match.group()
        return sig_bytes[:64] # قيمة احتياطية

# --- [ سيرفر الويب ] ---
@app.route('/')
def home():
    return "Abdo-AI Server is LIVE 🚀"

@app.route('/verify_now', methods=['GET', 'POST'])
def verify_now(): return jsonify({"status": "verified"})

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# --- [ واجهات الأزرار ] ---

def main_keyboard():
    m = telebot.types.InlineKeyboardMarkup(row_width=1)
    m.add(
        telebot.types.InlineKeyboardButton("🚀 تشفير Signature Bypass", callback_data="start_crypt"),
        telebot.types.InlineKeyboardButton("🛠 IDA Pro Menu (الخصائص)", callback_data="ida_menu"),
        telebot.types.InlineKeyboardButton("🌐 لوحة التحكم", url=DASHBOARD_URL)
    )
    return m

def ida_keyboard():
    m = telebot.types.InlineKeyboardMarkup(row_width=1)
    m.add(
        telebot.types.InlineKeyboardButton("🔓 فك تشفير الملفات (Unpack)", callback_data="ida_unpack"),
        telebot.types.InlineKeyboardButton("📊 استخراج الأوفستات العامة", callback_data="ida_general"),
        telebot.types.InlineKeyboardButton("💎 استخراج الأوفستات القوية (VIP)", callback_data="ida_strong"),
        telebot.types.InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data="back_main")
    )
    return m

# --- [ معالجة البوت ] ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "⚡️ **نظام ABDO TOP1 المطور**\nاختر من القائمة أدناه:", 
                     reply_markup=main_keyboard(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    chat_id = call.message.chat.id
    
    if call.data == "ida_menu":
        bot.edit_message_text("🛠 **قائمة خصائص IDA Pro**\nاختر نوع العملية:", 
                              chat_id, call.message.message_id, reply_markup=ida_keyboard(), parse_mode="Markdown")
    
    elif call.data == "back_main":
        bot.edit_message_text("⚡️ **القائمة الرئيسية**:", 
                              chat_id, call.message.message_id, reply_markup=main_keyboard(), parse_mode="Markdown")

    elif call.data == "start_crypt":
        user_data[chat_id] = {'mode': 'crypt', 'step': 'original'}
        bot.send_message(chat_id, "1️⃣ أرسل ملف الـ **3D الأصلي**:")

    elif call.data in ["ida_unpack", "ida_general", "ida_strong"]:
        user_data[chat_id] = {'mode': call.data}
        bot.send_message(chat_id, f"📥 أرسل الملف للتحليل عبر محرك IDA ({call.data}):")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    
    state = user_data[chat_id]
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    
    # --- [ مسار التشفير المطور ] ---
    if state.get('mode') == 'crypt':
        if state['step'] == 'original':
            state['step'] = 'sig'
            user_data[chat_id] = state
            bot.reply_to(message, "✅ تم استلام الأصلي.\n2️⃣ أرسل الآن ملف الـ **_CodeSignature** لاستخراج بصمة الـ 3D:")
        
        elif state['step'] == 'sig':
            state['signature_3d'] = AbdoBypassEngine.extract_3d_signature(downloaded)
            state['step'] = 'mod'
            user_data[chat_id] = state
            bot.reply_to(message, "✅ تم استخراج البصمة بنجاح.\n3️⃣ أرسل الآن **الملف المعدل** للتشفير النهائي:")
            
        elif state['step'] == 'mod':
            bot.reply_to(message, "⚙️ جاري التشفير والحقن ببصمة الـ 3D...")
            magic = b"UnityFS\x00\x00\x00\x00\x07"
            final = magic + state['signature_3d'] + downloaded
            out = io.BytesIO(final); out.name = f"Abdo_Bypass_{message.document.file_name}"
            bot.send_document(chat_id, out, caption="✅ تم التشفير بنظام Signature Bypass بنجاح!")
            del user_data[chat_id]

    # --- [ مسارات IDA Pro ] ---
    elif "ida" in state.get('mode'):
        mode = state.get('mode')
        report = []
        if mode == "ida_unpack":
            report.append("--- [ UNPACKING REPORT ] ---")
            if zipfile.is_zipfile(io.BytesIO(downloaded)):
                with zipfile.ZipFile(io.BytesIO(downloaded)) as z:
                    report.extend([f"Extracted: {n}" for n in z.namelist()])
            else: report.append("تم فحصه كـ Binary.")
        elif mode == "ida_general":
            report.extend(IDAProAdvanced.extract_all(downloaded))
        elif mode == "ida_strong":
            report.extend(IDAProAdvanced.extract_strong(downloaded))

        res_name = f"IDA_{mode}.txt"
        with open(res_name, "w", encoding="utf-8") as f: f.write("\n".join(report))
        with open(res_name, "rb") as f:
            bot.send_document(chat_id, f, caption=f"✅ اكتملت عملية IDA: {mode}")
        os.remove(res_name)
        del user_data[chat_id]

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling()
