import requests

def handle_gen(bot, message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ Use: <code>/gen 45717360 [qty]</code>", parse_mode="HTML")
        return
    bin_code = args[1][:16]
    qty = 10
    if len(args) > 2 and args[2].isdigit():
        qty = min(int(args[2]), 50)
    url = f"https://drlabapis.onrender.com/api/ccgenerator?bin={bin_code}&qty={qty}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200 and r.json().get("data"):
            cards = r.json()["data"]
            msg = "<b>Generated Cards</b>\n━━━━━━━━━━━━━━━━━━━━━━\n"
            msg += "\n".join([f"<code>{c}</code>" for c in cards])
            msg += f"\n━━━━━━━━━━━━━━━━━━━━━━\nTotal: <b>{len(cards)}</b>\n"
            msg += "Bot By: 𝗕𝗨𝗡𝗡𝗬 <a href='https://t.me/bunny2050'>@bunny2050</a>"
        else:
            msg = "❌ No cards generated. Invalid BIN or server error."
    except Exception as e:
        msg = f"❌ Error: {e}"
    bot.reply_to(message, msg, parse_mode="HTML")
