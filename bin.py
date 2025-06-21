import requests

def handle_bin(bot, message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ Use: <code>/bin 45717360</code>", parse_mode="HTML")
        return
    bin_code = args[1][:8]
    url = f"https://bins.antipublic.cc/bins/{bin_code}"
    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200 and resp.text.strip() and 'country' in resp.text:
            data = resp.json()
            msg = (
                f"<b>BIN Lookup</b> <code>{bin_code}</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"<b>Brand:</b> {data.get('brand', 'UNKNOWN')}\n"
                f"<b>Type:</b> {data.get('type', 'UNKNOWN')}\n"
                f"<b>Level:</b> {data.get('level', 'UNKNOWN')}\n"
                f"<b>Bank:</b> {data.get('bank', 'UNKNOWN')}\n"
                f"<b>Country:</b> {data.get('country', 'UNKNOWN')} {data.get('countryInfo', {}).get('emoji', '')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                "Bot By: 𝗕𝗨𝗡𝗡𝗬 <a href='https://t.me/bunny2050'>@bunny2050</a>"
            )
        else:
            msg = f"❌ BIN not found or unavailable for <code>{bin_code}</code>."
    except Exception as e:
        msg = f"❌ Error: {e}"
    bot.reply_to(message, msg, parse_mode="HTML")
