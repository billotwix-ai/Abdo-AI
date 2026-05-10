# -*- coding: utf-8 -*-
import telebot
import threading
import os
import io
from flask import Flask, request, jsonify

# --- [ الإعدادات الأساسية ] ---
TOKEN = '8617254929:AAGtY99XlCktp62gdPkWz7aNonDuvrLWjZc'
DASHBOARD_URL = "https://abdo-ai.onrender.com/" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_data = {}

# قاعدة بيانات مؤقتة لتسجيل الـ IP الذين أتموا التحقق
verified_ips = set()

# --- [ محرك التشفير الخارق - Titan Engine ] ---
class TitanHyperEngine:
    @staticmethod
    def hyper_crypt(mod_bytes, header):
        # بصمة Unity الرسمية لتجاوز الفحص (Bypass)
        magic_unity = b"UnityFS\x00\x00\x00\x00\x07"
        return magic_unity + header + mod_bytes

# --- [ سيرفر لوحة التحكم والتحقق الذكي ] ---
@app.route('/')
def home():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1 style='color:#00ff41;background-color:#000;text-align:center;padding:50px;'>Abdo-AI Server is LIVE 🚀</h1>"

# الربط مع الـ HTML: استقبال طلب التحقق وإرجاع النتيجة
@app.route('/verify_click', methods=['POST'])
def verify_click():
    try:
        user_ip = request.remote_addr
        verified_ips.add(user_ip) # تسجيل الشخص كـ "تم التحقق"
        return jsonify({"status": "success", "msg": "تم"})
    except Exception as e:
        return jsonify({"status": "fail", "msg": "اشترك وعد لاتمام العملية"})

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- [ واجهات الأزرار ] ---
def main_keyboard():
    m = telebot.types.InlineKeyboardMarkup(row_width=1)
    m.add(
        telebot.types.InlineKeyboardButton("🚀 تشفير Hyper Bypass (iOS)", callback_data="start_path"),
        telebot.types.InlineKeyboardButton("🌐 فتح لوحة تحكم Abdo-AI", url=DASHBOARD_URL)
    )
    return m

# --- [ أوامر ومعالجة البوت ] ---
@bot.message_handler(commands=['start'])
def start(message):
    msg = (
        "⚡️ **Abdo-AI Hyper Cloud v4.0**\n"
        "تم ربط نظام **ABDO TOP1** بنجاح.\n\n"
        "✅ الحالة: متصل بالسيرفر\n"
        "🔗 رابط التحقق: " + DASHBOARD_URL
    )
    bot.send_message(message.chat.id, msg, reply_markup=main_keyboard(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    chat_id = call.message.chat.id
    if call.data == "start_path":
        user_data[chat_id] = {'step': '3d'}
        bot.edit_message_text("1️⃣ أرسل ملف الـ **3D الأصلي** لسحب الهيدر:", chat_id, call.message.message_id)

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    state = user_data[chat_id]

    # منطق سحب الهيدر والتشفير
    if state['step'] == '3d':
        file_info = bot.get_file(message.document.file_id)
        file_bytes = bot.download_file(file_info.file_path)
        state['header'] = file_bytes[:32]
        state['step'] = 'mod'
        bot.reply_to(message, "✅ تم سحب التوقيع.\n2️⃣ أرسل الآن **الملف المعدل** للحقن النهائي:")

    elif state['step'] == 'mod':
        status_msg = bot.reply_to(message, "⚙️ جاري التشفير عبر سيرفر Abdo-AI...")
        
        file_info = bot.get_file(message.document.file_id)
        mod_bytes = bot.download_file(file_info.file_path)
        
        # تنفيذ التشفير
        final_file = TitanHyperEngine.hyper_crypt(mod_bytes, state['header'])
        
        out = io.BytesIO(final_file)
        out.name = f"Abdo_Crypted_{message.document.file_name}"
        
        bot.send_document(chat_id, out, caption="✅ **اكتمل التشفير بنجاح!**\nتم التخطي بنظام Titan.")
        del user_data[chat_id]

# --- [ التشغيل النهائي ] ---
if __name__ == "__main__":
    # تشغيل سيرفر Flask في خيط منفصل (Thread)
    threading.Thread(target=run_web, daemon=True).start()
    print("🚀 Server & Bot are running together...")
    # تشغيل البوت
    bot.infinity_polling()
