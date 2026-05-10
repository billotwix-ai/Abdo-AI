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
        # البحث عن بصمة الـ 3D داخل ملف التوقيع
        match = re.search(rb'.{10,64}\x33\x44', sig_bytes)
        return match.group() if match else sig_bytes[:64]

    @staticmethod
    def apply_bypass(mod_bytes, sig_data, header):
        magic = b"UnityFS\x00\x00\x00\x00\x07"
        # بايتات تشويش لمنع برامج Asset Studio من التعرف على الملف
        obfuscation = b"\x00\xff\x00\xff\xaa\xbb" 
        return magic + sig_data + header + obfuscation + mod_bytes

# ==========================================
# 3. كلاس محرك IDA Pro (التحليل المستقل)
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
# 4. كلاس واجهات الأزرار (مثل الصور تماماً)
# ==========================================
class InterfaceModule:
    @staticmethod
    def main_menu():
        m = telebot.types.InlineKeyboardMarkup(row_width=1)
        m.add(
            telebot.types.InlineKeyboardButton("🚀 صنع بوت خاص بك", callback_data="make_bot"),
            telebot.types.InlineKeyboardButton("🔓 فك حظر تليجرام", callback_data="unban_tele"),
            telebot.types.InlineKeyboardButton("🇰🇷 فك حظر كروبات", callback_data="unban_group"),
            telebot.types.InlineKeyboardButton("🛠 تشفير Signature Bypass", callback_data="btn_crypt"),
            telebot.types.InlineKeyboardButton("💎 خصائص IDA Pro", callback_data="btn_ida"),
            telebot.types.InlineKeyboardButton("📢 قناة الدمري واتساب", url="https://whatsapp.com/channel/your_link"),
            telebot.types.InlineKeyboardButton("⛩ انستجرام", url="https://instagram.com/your_link")
        )
        return m

    @staticmethod
    def ida_menu():
        m = telebot.types.InlineKeyboardMarkup(row_width=1)
        m.add(
            telebot.types.InlineKeyboardButton("🔓 Unpack (فك الملفات)", callback_data="ida_unpack"),
            telebot.types.InlineKeyboardButton("📊 الأوفستات العامة", callback_data="ida_general"),
            telebot.types.InlineKeyboardButton("💎 الأوفستات القوية (VIP)", callback_data="ida_strong"),
            telebot.types.InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data="btn_main")
        )
        return m

# ==========================================
# 5. منطق معالجة الرسائل والملفات
# ==========================================
@bot.message_handler(commands=['start'])
def welcome(message):
    welcome_msg = (
        "⚡️ **مرحباً بك في نظام ABDO TOP1 v6.0**\n"
        "تم تحديث المحركات لتشمل Bypass 3D و IDA Pro المطور.\n\n"
        "اختر المهمة المطلوبة من الأزرار أدناه:"
    )
    bot.send_message(message.chat.id, welcome_msg, 
                     reply_markup=InterfaceModule.main_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    chat_id = call.message.chat.id
    
    # قائمة IDA Pro
    if call.data == "btn_ida":
        bot.edit_message_text("🛠 **قائمة خصائص IDA Pro المتقدمة**\nاختر نوع التحليل المطلوب:", 
                              chat_id, call.message.message_id, 
                              reply_markup=InterfaceModule.ida_menu(), parse_mode="Markdown")
    
    # القائمة الرئيسية
    elif call.data == "btn_main":
        bot.edit_message_text("⚡️ **القائمة الرئيسية**\nاختر الوظيفة:", 
                              chat_id, call.message.message_id, 
                              reply_markup=InterfaceModule.main_menu(), parse_mode="Markdown")

    # بدء التشفير (3 خطوات)
    elif call.data == "btn_crypt":
        user_data[chat_id] = {'mode': 'crypt', 'step': 'original'}
        bot.send_message(chat_id, "1️⃣ أرسل **الملف الأصلي** لسحب الهيدر:")

    # أوامر أخرى (رسائل وهمية للأزرار الإضافية)
    elif call.data in ["make_bot", "unban_tele", "unban_group"]:
        bot.answer_callback_query(call.id, "هذه الميزة ستكون متاحة قريباً في التحديث القادم!", show_alert=True)

    # تفعيل أوضاع IDA
    elif call.data.startswith("ida_"):
        user_data[chat_id] = {'mode': call.data}
        bot.send_message(chat_id, f"📥 أرسل الملف الآن للبدء في عملية الـ {call.data.replace('ida_', '')}:")

@bot.message_handler(content_types=['document'])
def process_files(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    
    state = user_data[chat_id]
    file_bytes = bot.download_file(bot.get_file(message.document.file_id).file_path)

    # --- [ مسار التشفير الثلاثي ] ---
    if state.get('mode') == 'crypt':
        if state['step'] == 'original':
            state.update({'header': file_bytes[:32], 'step': 'sig'})
            bot.reply_to(message, "✅ تم سحب الهيدر.\n2️⃣ أرسل الآن ملف **_CodeSignature** لاستخراج بصمة الـ 3D:")
        
        elif state['step'] == 'sig':
            state.update({'sig_data': EncryptionModule.extract_3d_signature(file_bytes), 'step': 'mod'})
            bot.reply_to(message, "✅ تم استخراج البصمة بنجاح.\n3️⃣ أرسل الآن **الملف المعدل** للتشفير النهائي:")
            
        elif state['step'] == 'mod':
            bot.reply_to(message, "⚙️ جاري التشفير ومنع أدوات الاستخراج...")
            final = EncryptionModule.apply_bypass(file_bytes, state['sig_data'], state['header'])
            out = io.BytesIO(final); out.name = f"Crypt_ABDO_{message.document.file_name}"
            bot.send_document(chat_id, out, caption="✅ **تم التشفير بنجاح!**\nتم التخطي ومنع فتح الملف عبر Asset Studio.")
            del user_data[chat_id]

    # --- [ مسار IDA Pro ] ---
    elif "ida" in state.get('mode'):
        mode = state.get('mode')
        bot.reply_to(message, "⚙️ جاري تحليل الملف عبر محرك IDA...")
        
        if "unpack" in mode: report = IDAModule.run_unpack(file_bytes)
        elif "general" in mode: report = IDAModule.get_general_offsets(file_bytes)
        else: report = IDAModule.get_strong_offsets(file_bytes)
        
        res_file = io.BytesIO(report.encode()); res_file.name = f"IDA_Report_{mode}.txt"
        bot.send_document(chat_id, res_file, caption=f"✅ اكتمل تحليل IDA بنجاح.")
        del user_data[chat_id]

# ==========================================
# 6. تشغيل السيرفر والبوت
# ==========================================
@app.route('/')
def home(): return "Abdo-AI Organized Server LIVE 🚀"

if __name__ == "__main__":
    # تشغيل Flask في خيط منفصل لبيئة Render/Heroku
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    print("🚀 البوت يعمل الآن بنفس واجهة الصور...")
    bot.infinity_polling()
