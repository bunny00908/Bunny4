import time

def handle_status(bot, message):
    start = time.time()
    sent = bot.reply_to(message, "⏳ Checking bot status...")
    ms = int((time.time() - start) * 1000)
    msg = (
        "<b>🤖 Bunny Bot Status</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "✅ <b>Status:</b> <code>Online</code>\n"
        f"⚡️ <b>Ping:</b> <code>{ms} ms</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Bot By: 𝗕𝗨𝗡𝗡𝗬 <a href='https://t.me/bunny2050'>@bunny2050</a>"
    )
    bot.edit_message_text(msg, sent.chat.id, sent.message_id, parse_mode="HTML")
