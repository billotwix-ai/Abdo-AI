# -*- coding: utf-8 -*-
import telebot
import threading
import io
import re
from flask import Flask

# ==========================================
# 1. الإعدادات الأساسية
# ==========================================
TOKEN = '8617254929:AAGtY99XlCktp62gdPkWz7aNonDuvrLWjZc'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_data = {}

# ==========================================
# 2. محرك العمليات (تشفير وفك تشفير)
# ==========================================
class EngineModule:
    @staticmethod
    def extract_3d_signature(sig_bytes):
        match = re.search(rb'.{10,64}\x33\x44', sig_bytes)
        return match.group() if match else sig_bytes[:64]

    @staticmethod
    def apply_crypt(mod_bytes, sig_data, header):
        # تشفير وحماية (إضافة بايتات كسر البرامج)
        magic = b"UnityFS\x00\x00\x00\x00\x07"
        obfuscation = b"\x00\xff\x00\xff\xaa\xbb" 
        return magic + sig_data + header + obfuscation + mod_bytes

    @staticmethod
    def apply_decrypt(mod_bytes, sig_data, header):
        # فك تشفير (إرجاع الملف لهيكلة نظيفة تقرأها البرامج)
        magic = b"UnityFS\x00\x00\x00\x00\x07"
        return magic + sig_data + header + mod_bytes

# ==========================================
# 3. واجهات الأزرار
# ==========================================
class InterfaceModule:
    @staticmethod
    def main_menu():
        m = telebot.types.InlineKeyboardMarkup(row_width=1)
        m.add(
            telebot.types.InlineKeyboardButton("🔐 تشفير (Bypass 3D)", callback_data="btn_crypt"),
            telebot.types.InlineKeyboardButton("🔓 فك التشفير (Assets Studio)", callback_data="btn_decrypt")
        )
        return m

    @staticmethod
    def back_button():
        m = telebot.types.InlineKeyboardMarkup()
        m.add(telebot.types.InlineKeyboardButton("⬅️ إلغاء والعودة للقائمة", callback_data="btn_main"))
        return m

# ==========================================
# 4. منطق البوت
# ==========================================
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "⚡️ **مرحباً بك في محرك ABDO TOP1**\nاختر العملية المطلوبة:", 
                     reply_markup=InterfaceModule.main_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    chat_id = call.message.chat.id
    
    if call.data == "btn_main":
        user_data.pop(chat_id, None)
        bot.edit_message_text("⚡️ تم الإلغاء. اختر العملية:", chat_id, call.message.message_id, 
                              reply_markup=InterfaceModule.main_menu())

    elif call.data == "btn_crypt":
        user_data[chat_id] = {'mode': 'crypt', 'step': 'original'}
        bot.send_message(chat_id, "🔐 **وضع التشفير:**\n1️⃣ أرسل **الملف الأصلي**:", reply_markup=InterfaceModule.back_button())

    elif call.data == "btn_decrypt":
        user_data[chat_id] = {'mode': 'decrypt', 'step': 'original'}
        bot.send_message(chat_id, "🔓 **وضع فك التشفير:**\n1️⃣ أرسل **الملف المشفر**:", reply_markup=InterfaceModule.back_button())

@bot.message_handler(content_types=['document'])
def process_files(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    
    state = user_data[chat_id]
    mode = state['mode']
    file_bytes = bot.download_file(bot.get_file(message.document.file_id).file_path)

    if state['step'] == 'original':
        state.update({'header': file_bytes[:32], 'step': 'sig'})
        bot.reply_to(message, "✅ تم الحفظ.\n2️⃣ أرسل ملف **_CodeSignature**:", reply_markup=InterfaceModule.back_button())
    
    elif state['step'] == 'sig':
        state.update({'sig_data': EngineModule.extract_3d_signature(file_bytes), 'step': 'mod'})
        bot.reply_to(message, "✅ تم سحب البصمة.\n3️⃣ أرسل **الملف الأخير** للتنفيذ:", reply_markup=InterfaceModule.back_button())
        
    elif state['step'] == 'mod':
        bot.reply_to(message, "⚙️ جاري المعالجة...")
        if mode == 'crypt':
            final = EngineModule.apply_crypt(file_bytes, state['sig_data'], state['header'])
            cap = "✅ تم التشفير والحماية بنجاح!"
        else:
            final = EngineModule.apply_decrypt(file_bytes, state['sig_data'], state['header'])
            cap = "✅ تم فك التشفير (جاهز لـ Assets Studio)!"
            
        out = io.BytesIO(final); out.name = f"{mode.upper()}_{message.document.file_name}"
        bot.send_document(chat_id, out, caption=cap)
        del user_data[chat_id]

# ==========================================
# 5. التشغيل
# ==========================================
@app.route('/')
def home(): return "Server Live 🚀"

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    bot.infinity_polling()
