import requests

def handle_fake(bot, message):
    args = message.text.split()
    country = args[1].upper() if len(args) > 1 else 'US'
    url = f"https://randomuser.me/api/?nat={country}"
    try:
        r = requests.get(url, timeout=7)
        if r.status_code == 200:
            user = r.json()['results'][0]
            msg = (
                "<b>Fake Identity</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"<b>Name:</b> {user['name']['first']} {user['name']['last']}\n"
                f"<b>Country:</b> {user['location']['country']}\n"
                f"<b>State:</b> {user['location']['state']}\n"
                f"<b>City:</b> {user['location']['city']}\n"
                f"<b>Street:</b> {user['location']['street']['number']} {user['location']['street']['name']}\n"
                f"<b>Zip:</b> {user['location']['postcode']}\n"
                f"<b>Email:</b> {user['email']}\n"
                f"<b>Phone:</b> {user['phone']}\n"
                f"<b>DOB:</b> {user['dob']['date'][:10]}\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "Bot By: 𝗕𝗨𝗡𝗡𝗬 <a href='https://t.me/bunny2050'>@bunny2050</a>"
            )
        else:
            msg = "❌ Could not fetch fake identity. Try a different country code."
    except Exception as e:
        msg = f"❌ Error: {e}"
    bot.reply_to(message, msg, parse_mode="HTML")
