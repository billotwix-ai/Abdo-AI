# -*- coding: utf-8 -*-
import telebot
import io
import hashlib
import time
import threading
from flask import Flask

# --- [إعدادات الخادم] ---
TOKEN = '8617254929:AAGtY99XlCktp62gdPkWz7aNonDuvrLWjZc'

# الرابط الجديد الذي طلبته
MY_DASHBOARD_URL = "https://your-private-dashboard.com/" 

bot = telebot.TeleBot(TOKEN, threaded=True)
user_data = {}

# --- [سيرفر الويب للوحة التحكم] ---
app = Flask(__name__)
@app.route('/')
def index():
    try:
        # سيقوم السيرفر بعرض ملف index.html الموجود في مستودعك
        return open("index.html", "r", encoding="utf-8").read()
    except:
        return "Titan Server Dashboard is Online."

def run_web():
    # منفذ 10000 متوافق مع Render
    app.run(host='0.0.0.0', port=10000)

# --- [محرك التشفير] ---
class TitanUltimateEngine:
    @staticmethod
    def hyper_crypt(mod_bytes, header):
        magic_unity = b"UnityFS\x00\x00\x00\x00\x07"
        # حقن البصمة الأصلية مع البيانات المعدلة
        return magic_unity + header + mod_bytes

# --- [الواجهات] ---
def main_keyboard():
    m = telebot.types.InlineKeyboardMarkup(row_width=1)
    m.add(
        telebot.types.InlineKeyboardButton("🚀 تشفير Hyper Bypass", callback_data="start_path"),
        telebot.types.InlineKeyboardButton("🌐 فتح لوحة تحكم خادمي", url=MY_DASHBOARD_URL)
    )
    return m

def back_home_btn():
    m = telebot.types.InlineKeyboardMarkup()
    m.add(telebot.types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="home"))
    return m

# --- [المعالجة] ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        "⚡️ **Titan Hyper Cloud Ready**\nخادمك الخاص متصل الآن ويعمل بكفاءة.",
        reply_markup=main_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    chat_id = call.message.chat.id
    if call.data == "start_path":
        user_data[chat_id] = {'step': '3d'}
        bot.edit_message_text("1️⃣ أرسل ملف الـ **3D الأصلي** لجلب الهيدر:", chat_id, call.message.message_id)
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
            state['header'] = file_bytes[:32]
            state['step'] = 'res'
            bot.reply_to(message, "✅ تم جلب الهيدر بنجاح.\n2️⃣ أرسل الآن ملف **CodeResources**:")
        
        elif state['step'] == 'res':
            state['step'] = 'ver'
            bot.reply_to(message, "3️⃣ أرسل رقم التحديث (مثل OB53):")

        elif state['step'] == 'mod':
            status = bot.reply_to(message, "⚙️ جاري معالجة الملف في السيرفر وتطبيق التشفير...")
            final = TitanUltimateEngine.hyper_crypt(file_bytes, state['header'])
            
            out = io.BytesIO(final)
            out.name = f"Titan_Crypted_{message.document.file_name}"
            
            # إرسال الملف المشفر
            bot.send_document(chat_id, out, caption="✅ **تم التشفير بنجاح!**\nالملف جاهز للاستبدال في مسار اللعبة.")
            
            # إرسال رسالة العودة للقائمة تلقائياً
            bot.send_message(chat_id, "✨ العملية اكتملت. هل تود القيام بعملية أخرى؟", reply_markup=back_home_btn())
            del user_data[chat_id]

    elif message.content_type == 'text' and state['step'] == 'ver':
        state['step'] = 'mod'
        bot.reply_to(message, "4️⃣ أرسل الآن **الملف المعدل** للحقن النهائي:")

# --- [التشغيل] ---
if __name__ == "__main__":
    # تشغيل واجهة الويب في الخلفية لتفادي تعليق البوت
    threading.Thread(target=run_web, daemon=True).start()
    print("🚀 Server & Dashboard (URL Updated) are Online!")
    bot.infinity_polling()
