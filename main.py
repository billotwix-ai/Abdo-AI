# -*- coding: utf-8 -*-
import telebot
import threading
import os
import io
import hashlib
from flask import Flask

# --- [ الإعدادات الأساسية ] ---
TOKEN = '8617254929:AAGtY99XlCktp62gdPkWz7aNonDuvrLWjZc'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_data = {}

# --- [ محرك التشفير الخارق - Titan Engine ] ---
class TitanHyperEngine:
    @staticmethod
    def hyper_crypt(mod_bytes, header):
        magic_unity = b"UnityFS\x00\x00\x00\x00\x07"
        # دمج الهيدر الأصلي مع البيانات المعدلة لضمان التوافق
        return magic_unity + header + mod_bytes

# --- [ سيرفر لوحة التحكم ] ---
@app.route('/')
def home():
    try:
        # قراءة ملف index.html وعرضه كواجهة للموقع
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1 style='color:green;text-align:center;font-family:monospace;'>Titan Server is Active & Running!</h1>"

def run_web():
    # الحصول على المنفذ تلقائياً من Render (بشكل أساسي 10000)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- [ واجهات الأزرار ] ---
def main_keyboard(dashboard_url):
    m = telebot.types.InlineKeyboardMarkup(row_width=1)
    m.add(
        telebot.types.InlineKeyboardButton("🚀 تشفير Hyper Bypass", callback_data="start_path"),
        telebot.types.InlineKeyboardButton("🌐 فتح لوحة التحكم الخارقة", url=dashboard_url)
    )
    return m

def back_home_btn():
    m = telebot.types.InlineKeyboardMarkup()
    m.add(telebot.types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="home"))
    return m

# --- [ أوامر ومعالجة البوت ] ---
@bot.message_handler(commands=['start'])
def start(message):
    # ملاحظة: ضع رابط Render الخاص بك هنا ليعمل الزر بشكل صحيح
    dashboard_url = "https://your-app-name.onrender.com" 
    
    msg = (
        "⚡️ **Titan Hyper Cloud v4.0**\n"
        "تم الاتصال بالخادم بنجاح.\n\n"
        "📍 الحالة: متصل (Live)\n"
        "⚙️ المحرك: Bypass iOS Ready"
    )
    bot.send_message(message.chat.id, msg, reply_markup=main_keyboard(dashboard_url), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    chat_id = call.message.chat.id
    if call.data == "start_path":
        user_data[chat_id] = {'step': '3d'}
        bot.edit_message_text("1️⃣ أرسل ملف الـ **3D الأصلي** لجلب الهيدر:", chat_id, call.message.message_id)
    elif call.data == "home":
        user_data.pop(chat_id, None)
        bot.edit_message_text("🛠 **قائمة التحكم الرئيسية**", chat_id, call.message.message_id, reply_markup=main_keyboard("https://your-app-name.onrender.com"))

@bot.message_handler(content_types=['document', 'text'])
def workflow(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    state = user_data[chat_id]

    if message.content_type == 'document':
        file_bytes = bot.download_file(bot.get_file(message.document.file_id).file_path)
        
        if state['step'] == '3d':
            state['header'] = file_bytes[:32]
            state['step'] = 'res'
            bot.reply_to(message, "✅ تم جلب الهيدر بنجاح.\n2️⃣ أرسل الآن ملف **CodeResources**:")
        
        elif state['step'] == 'res':
            state['step'] =
