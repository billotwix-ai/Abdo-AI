# -*- coding: utf-8 -*-
import telebot
import threading
import os
import io
import hashlib
from flask import Flask

# --- [ الإعدادات الأساسية ] ---
TOKEN = '8617254929:AAGtY99XlCktp62gdPkWz7aNonDuvrLWjZc'
# تم تحديث الرابط الفعلي لخادمك هنا
DASHBOARD_URL = "https://abdo-ai.onrender.com/" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_data = {}

# --- [ محرك التشفير الخارق - Titan Engine ] ---
class TitanHyperEngine:
    @staticmethod
    def hyper_crypt(mod_bytes, header):
        # بصمة Unity الرسمية لتجاوز الفحص (Bypass)
        magic_unity = b"UnityFS\x00\x00\x00\x00\x07"
        return magic_unity + header + mod_bytes

# --- [ سيرفر لوحة التحكم ] ---
@app.route('/')
def home():
    try:
        # عرض ملف index.html الخاص بك
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1 style='color:#00ff41;background-color:#000;text-align:center;padding:50px;font-family:monospace;'>Abdo-AI Server is LIVE 🚀</h1>"

def run_web():
    # المنفذ الخاص ببيئة Render
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

def back_home_btn():
    m = telebot.types.InlineKeyboardMarkup()
    m.add(telebot.types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="home"))
    return m

# --- [ أوامر ومعالجة البوت ] ---
@bot.message_handler(commands=['start'])
def start(message):
    msg = (
        "⚡️ **Abdo-AI Hyper Cloud v4.0**\n"
        "مرحباً بك! خادمك الخاص متصل الآن.\n\n"
        "🔗 رابط الخادم: " + DASHBOARD_URL + "\n"
        "⚙️ الحالة: جاهز لتشفير ملفات OB53"
    )
    bot.send_message(message.chat.id, msg, reply_markup=main_keyboard(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    chat_id = call.message.chat.id
    if call.data == "start_path":
        user_data[chat_id] = {'step': '3d'}
        bot.edit_message_text("1️⃣ أرسل ملف الـ **3D الأصلي** لسحب الهيدر:", chat_id, call.message.message_id)
    elif call.data == "home":
        user_data.pop(chat_id, None)
        bot.edit_message_text("🛠 **قائمة التحكم الرئيسية**", chat_id, call.message.message_id, reply_markup=main_keyboard())

@bot.message_handler(content_types=['document', 'text'])
def workflow(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    state = user_data[chat_id]

    if message.content_type == 'document':
        file_bytes = bot.download_file(bot.get_file(message.document.file_id).file_path)
        
        if state['step'] == '3d':
            state['header'] = file_bytes[:32] # سحب أول 32 بايت كبصمة
            state['step'] = 'res'
            bot.reply_to(message, "✅ تم سحب التوقيع الأصلي.\n2️⃣ أرسل الآن ملف **CodeResources**:")
        
        elif state['step'] == 'res':
            state['step'] = 'ver'
            bot.reply_to(message, "3️⃣ أرسل رقم إصدار التحديث (مثل OB53):")

        elif state['step'] == 'mod':
            status = bot.reply_to(message, "⚙️ جاري التشفير عبر سيرفر Abdo-AI...")
            final = TitanHyperEngine.hyper_crypt(file_bytes, state['header'])
            
            out = io.BytesIO(final)
            out.name = f"Abdo_Crypted_{message.document.file_name}"
            
            bot.send_document(chat_id, out, caption="✅ **اكتمل التشفير الخارق!**\nالملف جاهز للاستبدال الآن.")
            bot.send_message(chat_id, "✨ هل تود تشفير ملف آخر؟", reply_markup=back_home_btn())
            del user_data[chat_id]

    elif message.content_type == 'text' and state['step'] == 'ver':
        state['step'] = 'mod'
        bot.reply_to(message, "4️⃣ أرسل الآن **الملف المعدل** للحقن النهائي:")

# --- [ التشغيل المتوازي ] ---
if __name__ == "__main__":
    # تشغيل الموقع في الخلفية
    threading.Thread(target=run_web, daemon=True).start()
    
    print("🚀 Abdo-AI Server is ONLINE")
    # تشغيل البوت في الواجهة
    bot.infinity_polling()
