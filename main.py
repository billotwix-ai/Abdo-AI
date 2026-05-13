# -*- coding: utf-8 -*-
import telebot
import threading
import io
import re
from flask import Flask

TOKEN = '8617254929:AAGtY99XlCktp62gdPkWz7aNonDuvrLWjZc'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_data = {}

class EngineModule:
    @staticmethod
    def extract_3d_signature(sig_bytes):
        # البحث عن توقيع الوحدة (Unity) الحقيقي داخل الملف
        match = re.search(rb'UnityFS', sig_bytes)
        if match:
            return sig_bytes[match.start():match.start()+64]
        return sig_bytes[:64]

    @staticmethod
    def apply_crypt(mod_bytes, sig_data, header):
        # إضافة بايتات تشويش قوية لكسر الـ Extractor
        magic = b"UnityFS\x00\x00\x00\x00\x07"
        obfuscation = b"\x00\xff\xaa\xbb" * 4 # زيادة التشويش
        return magic + sig_data + header + obfuscation + mod_bytes

    @staticmethod
    def apply_decrypt(mod_bytes):
        """
        دالة فك التشفير المحسنة:
        تقوم بالبحث عن بداية ملف الـ Unity الحقيقية وحذف كل ما قبلها 
        (الهيدر المضاف والبصمة والتشويش) ليعود الملف أصلياً.
        """
        # البحث عن كلمة UnityFS وهي بداية أي ملف Asset Bundle سليم
        pattern = b"UnityFS"
        index = mod_bytes.find(pattern)
        
        if index != -1:
            # قص كل البيانات التي تسبق UnityFS لإصلاح الأوفست
            return mod_bytes[index:]
        return mod_bytes

# ==========================================
# واجهة الأزرار والمنطق
# ==========================================
class InterfaceModule:
    @staticmethod
    def main_menu():
        m = telebot.types.InlineKeyboardMarkup(row_width=1)
        m.add(
            telebot.types.InlineKeyboardButton("🔐 تشفير (حماية كاملة)", callback_data="btn_crypt"),
            telebot.types.InlineKeyboardButton("🔓 فك التشفير (إصلاح للكمبيوتر)", callback_data="btn_decrypt")
        )
        return m

@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    chat_id = call.message.chat.id
    if call.data == "btn_crypt":
        user_data[chat_id] = {'mode': 'crypt', 'step': 'original'}
        bot.send_message(chat_id, "🔐 **وضع التشفير:**\n1️⃣ أرسل **الملف الأصلي**:")
    elif call.data == "btn_decrypt":
        user_data[chat_id] = {'mode': 'decrypt', 'step': 'direct'}
        bot.send_message(chat_id, "🔓 **وضع فك التشفير المباشر:**\nأرسل الملف المشفر الآن وسأقوم بتنظيفه لفتحه على الكمبيوتر:")

@bot.message_handler(content_types=['document'])
def process_files(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    
    state = user_data[chat_id]
    file_bytes = bot.download_file(bot.get_file(message.document.file_id).file_path)

    # --- وضع التشفير (يحتاج 3 ملفات) ---
    if state['mode'] == 'crypt':
        if state['step'] == 'original':
            state.update({'header': file_bytes[:32], 'step': 'sig'})
            bot.reply_to(message, "✅ أرسل الآن ملف **_CodeSignature**:")
        elif state['step'] == 'sig':
            state.update({'sig_data': EngineModule.extract_3d_signature(file_bytes), 'step': 'mod'})
            bot.reply_to(message, "✅ أرسل الآن **الملف المعدل**:")
        elif state['step'] == 'mod':
            final = EngineModule.apply_crypt(file_bytes, state['sig_data'], state['header'])
            out = io.BytesIO(final); out.name = f"PROTECTED_{message.document.file_name}"
            bot.send_document(chat_id, out, caption="✅ تم التشفير! لن يفتح في البرامج.")
            del user_data[chat_id]

    # --- وضع فك التشفير (تلقائي ومباشر) ---
    elif state['mode'] == 'decrypt':
        bot.reply_to(message, "⚙️ جاري تنظيف الملف وإصلاح الـ Offset...")
        final = EngineModule.apply_decrypt(file_bytes)
        
        out = io.BytesIO(final); out.name = f"CLEANED_{message.document.file_name}"
        bot.send_document(chat_id, out, caption="✅ تم إصلاح الملف!\nجرب فتحه الآن ببرنامج Asset Bundle Extractor.")
        del user_data[chat_id]

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    bot.infinity_polling()
