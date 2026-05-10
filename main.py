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

# --- [ محرك التشفير Titan - النسخة الأصلية المختصرة ] ---
class TitanHyperEngine:
    @staticmethod
    def hyper_crypt(mod_bytes, header):
        magic_unity = b"UnityFS\x00\x00\x00\x00\x07"
        return magic_unity + header + mod_bytes

# --- [ محرك IDA Pro المستقل ] ---
class IDAProEngine:
    @staticmethod
    def deep_scan(file_bytes):
        # البحث عن أنماط الأوفستات والقيم البرمجية (حتى 1500 أوفست)
        patterns = [rb'\x00\x00[\x00-\xFF]{2,4}', rb'\x48\x89\x5C\x24', rb'\x08\xD0\x4D\xE2']
        found_offsets = []
        for p in patterns: found_offsets.extend(re.findall(p, file_bytes))
        unique = sorted(list(set(found_offsets)))
        return [f"[IDA_PRO_ADDR] -> 0x{o.hex().upper()} | VALID" for o in unique[:1500]]

    @staticmethod
    def analyze(file_path):
        results = ["--- [ IDA PRO DEEP ANALYSIS - ABDO TOP1 ] ---\n"]
        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path, 'r') as z:
                # تحليل أول ملف برمجي داخل الأرشيف
                with z.open(z.namelist()[0]) as f:
                    results.extend(IDAProEngine.deep_scan(f.read(2000000)))
        else:
            with open(file_path, 'rb') as f:
                results.extend(IDAProEngine.deep_scan(f.read()))
        return "\n".join(results)

# --- [ سيرفر الويب والتحقق ] ---
@app.route('/')
def home():
    try:
        with open("index.html", "r", encoding="utf-8") as f: return f.read()
    except: return "Abdo-AI Server is LIVE 🚀"

@app.route('/verify_now', methods=['GET', 'POST'])
def verify_now(): return jsonify({"status": "verified"})

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- [ واجهة الأزرار الرسمية ] ---
def main_keyboard():
    m = telebot.types.InlineKeyboardMarkup(row_width=1)
    m.add(
        telebot.types.InlineKeyboardButton("🚀 تشفير Titan Bypass", callback_data="start_crypt"),
        telebot.types.InlineKeyboardButton("🛠 IDA Pro Analysis", callback_data="start_ida"),
        telebot.types.InlineKeyboardButton("🌐 لوحة التحكم", url=DASHBOARD_URL)
    )
    return m

# --- [ معالجة البوت ] ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "⚡️ **نظام ABDO TOP1 المطور v7.0**\nتم فصل محرك IDA Pro عن نظام التشفير بنجاح.", 
                     reply_markup=main_keyboard(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    chat_id = call.message.chat.id
    if call.data == "start_crypt":
        # إعادة تفعيل نظام التشفير الأصلي 100%
        user_data[chat_id] = {'mode': 'crypt', 'step': '3d'}
        bot.edit_message_text("1️⃣ أرسل ملف الـ **3D الأصلي** لسحب الهيدر:", chat_id, call.message.message_id)
    
    elif call.data == "start_ida":
        # تفعيل نظام IDA Pro المستقل
        user_data[chat_id] = {'mode': 'ida'}
        bot.edit_message_text("📥 أرسل الملف المطلوب تحليله عبر محرك IDA Pro:", chat_id, call.message.message_id)

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    
    state = user_data[chat_id]

    # --- [ مسار التشفير الصافي ] ---
    if state.get('mode') == 'crypt':
        if state['step'] == '3d':
            file_info = bot.get_file(message.document.file_id)
            file_bytes = bot.download_file(file_info.file_path)
            state['header'] = file_bytes[:32]
            state['step'] = 'mod'
            user_data[chat_id] = state # حفظ التقدم
            bot.reply_to(message, "✅ تم سحب الهيدر.\n2️⃣ أرسل الآن **الملف المعدل** للحقن:")

        elif state['step'] == 'mod':
            bot.reply_to(message, "⚙️ جاري التشفير...")
            file_info = bot.get_file(message.document.file_id)
            mod_bytes = bot.download_file(file_info.file_path)
            
            final_file = TitanHyperEngine.hyper_crypt(mod_bytes, state['header'])
            out = io.BytesIO(final_file)
            out.name = f"Crypted_{message.document.file_name}"
            
            bot.send_document(chat_id, out, caption="✅ **تم التشفير بنجاح!**")
            del user_data[chat_id]

    # --- [ مسار IDA Pro المستقل ] ---
    elif state.get('mode') == 'ida':
        msg = bot.reply_to(message, "⚙️ جاري تحليل الأوفستات عبر IDA Pro...")
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        temp_name = message.document.file_name
        with open(temp_name, 'wb') as f: f.write(downloaded)
        
        try:
            report_content = IDAProEngine.analyze(temp_name)
            report_file = f"IDA_Analysis_{temp_name}.txt"
            with open(report_file, "w", encoding="utf-8") as f: f.write(report_content)
            
            with open(report_file, "rb") as f:
                bot.send_document(chat_id, f, caption=f"✅ نتيجة تحليل IDA Pro لملف: {temp_name}")
            
            os.remove(temp_name)
            os.remove(report_file)
            del user_data[chat_id]
        except Exception as e:
            bot.reply_to(message, f"❌ خطأ في التحليل: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    print("🚀 Clean Build: Crypt and IDA are now separated!")
    bot.infinity_polling()
