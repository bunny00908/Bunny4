import re
import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from p import check_card

# --- Single Card Check: /chk ---
def handle_chk(bot, message):
    args = message.text.split(None, 1)
    if len(args) < 2 or "|" not in args[1]:
        bot.reply_to(message, (
            "❌ Send as: <code>/chk 4556737586899855|12|2026|123</code>"
        ), parse_mode="HTML")
        return
    card_line = args[1].strip()
    if card_line.count('|') != 3 or "\n" in card_line:
        bot.reply_to(message, (
            "❌ Only ONE card per /chk. Use /mchk or /chktxt for more."
        ), parse_mode="HTML")
        return

    reply_msg = bot.reply_to(message, "🔄 <b>Processing...</b>", parse_mode="HTML")
    def check_and_reply():
        try:
            result = check_card(card_line)
            # Make sure card is in <code>
            result = re.sub(
                r"(\d{12,19}\|\d{1,2}\|\d{2,4}\|\d{3,4})",
                r"<code>\1</code>", result
            )
            result = result.replace(
                "Bot By: @Mod_By_Kamal",
                "Bot By: 𝗕𝗨𝗡𝗡𝗬 <a href='https://t.me/bunny2050'>@bunny2050</a>"
            )
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("OK", callback_data="close"))
            bot.edit_message_text(result, message.chat.id, reply_msg.message_id, parse_mode="HTML", reply_markup=kb)
        except Exception as e:
            bot.edit_message_text(f"❌ Error: {e}", message.chat.id, reply_msg.message_id)
    threading.Thread(target=check_and_reply).start()


# --- Mass Card Check: /mchk ---
def handle_mchk(bot, message):
    # Get card list from reply or message
    cards_text = ""
    if message.reply_to_message and message.reply_to_message.text:
        cards_text = message.reply_to_message.text
    else:
        args = message.text.split(None, 1)
        if len(args) > 1:
            cards_text = args[1]
    # Parse cards, max 15
    card_lines = [line.strip() for line in cards_text.splitlines() if "|" in line]
    if not card_lines:
        bot.reply_to(message, "❌ No cards found!")
        return
    if len(card_lines) > 15:
        bot.reply_to(message, "❌ Max 15 cards at once with /mchk!")
        return

    approved = 0
    declined = 0
    checked = 0
    total = len(card_lines)

    # Initial status panel
    status_markup = InlineKeyboardMarkup(row_width=2)
    status_markup.add(
        InlineKeyboardButton(f"APPROVED {approved} 🔥", callback_data="none"),
        InlineKeyboardButton(f"DECLINED {declined} ❌", callback_data="none"),
        InlineKeyboardButton(f"TOTAL CHECKED {checked}", callback_data="none"),
        InlineKeyboardButton(f"TOTAL {total} ✅", callback_data="none"),
    )
    status_markup.add(InlineKeyboardButton("Close", callback_data="close"))

    status_msg = bot.send_message(
        message.chat.id,
        "━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=status_markup
    )

    def mass_check():
        nonlocal approved, declined, checked
        for card in card_lines:
            try:
                result = check_card(card)
                # Always in <code>
                result = re.sub(
                    r"(\d{12,19}\|\d{1,2}\|\d{2,4}\|\d{3,4})",
                    r"<code>\1</code>", result
                )
                result = result.replace(
                    "Bot By: @Mod_By_Kamal",
                    "Bot By: 𝗕𝗨𝗡𝗡𝗬 <a href='https://t.me/bunny2050'>@bunny2050</a>"
                )
                if "APPROVED" in result:
                    approved += 1
                    bot.send_message(message.chat.id, result, parse_mode="HTML")
                else:
                    declined += 1
                checked += 1
                # Live update buttons only
                status_markup = InlineKeyboardMarkup(row_width=2)
                status_markup.add(
                    InlineKeyboardButton(f"APPROVED {approved} 🔥", callback_data="none"),
                    InlineKeyboardButton(f"DECLINED {declined} ❌", callback_data="none"),
                    InlineKeyboardButton(f"TOTAL CHECKED {checked}", callback_data="none"),
                    InlineKeyboardButton(f"TOTAL {total} ✅", callback_data="none"),
                )
                status_markup.add(InlineKeyboardButton("Close", callback_data="close"))
                try:
                    bot.edit_message_reply_markup(
                        status_msg.chat.id,
                        status_msg.message_id,
                        reply_markup=status_markup
                    )
                except Exception:
                    pass
            except Exception:
                declined += 1
                checked += 1
        # Final panel (same as above)
        status_markup = InlineKeyboardMarkup(row_width=2)
        status_markup.add(
            InlineKeyboardButton(f"APPROVED {approved} 🔥", callback_data="none"),
            InlineKeyboardButton(f"DECLINED {declined} ❌", callback_data="none"),
            InlineKeyboardButton(f"TOTAL CHECKED {checked}", callback_data="none"),
            InlineKeyboardButton(f"TOTAL {total} ✅", callback_data="none"),
        )
        status_markup.add(InlineKeyboardButton("Close", callback_data="close"))
        try:
            bot.edit_message_reply_markup(
                status_msg.chat.id,
                status_msg.message_id,
                reply_markup=status_markup
            )
        except Exception:
            pass

    threading.Thread(target=mass_check).start()

# --- Check from .txt file: /chktxt ---
def handle_chktxt(bot, message):
    if not message.document:
        bot.reply_to(message, "❌ Send a .txt file with one card per line.")
        return
    # Download file
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        lines = downloaded_file.decode('utf-8', errors='ignore').splitlines()
        card_lines = [line.strip() for line in lines if "|" in line]
    except Exception as e:
        bot.reply_to(message, f"❌ Could not read file: {e}")
        return
    if not card_lines:
        bot.reply_to(message, "❌ No valid cards found in file!")
        return
    if len(card_lines) > 500:
        bot.reply_to(message, "❌ Max 500 cards in one file with /chktxt!")
        return

    approved = 0
    declined = 0
    checked = 0
    total = len(card_lines)

    # Initial status panel
    status_markup = InlineKeyboardMarkup(row_width=2)
    status_markup.add(
        InlineKeyboardButton(f"APPROVED {approved} 🔥", callback_data="none"),
        InlineKeyboardButton(f"DECLINED {declined} ❌", callback_data="none"),
        InlineKeyboardButton(f"TOTAL CHECKED {checked}", callback_data="none"),
        InlineKeyboardButton(f"TOTAL {total} ✅", callback_data="none"),
    )
    status_markup.add(InlineKeyboardButton("Close", callback_data="close"))

    status_msg = bot.send_message(
        message.chat.id,
        "━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=status_markup
    )

    def txt_check():
        nonlocal approved, declined, checked
        for card in card_lines:
            try:
                result = check_card(card)
                result = re.sub(
                    r"(\d{12,19}\|\d{1,2}\|\d{2,4}\|\d{3,4})",
                    r"<code>\1</code>", result
                )
                result = result.replace(
                    "Bot By: @Mod_By_Kamal",
                    "Bot By: 𝗕𝗨𝗡𝗡𝗬 <a href='https://t.me/bunny2050'>@bunny2050</a>"
                )
                if "APPROVED" in result:
                    approved += 1
                    bot.send_message(message.chat.id, result, parse_mode="HTML")
                else:
                    declined += 1
                checked += 1
                # Live update buttons only
                status_markup = InlineKeyboardMarkup(row_width=2)
                status_markup.add(
                    InlineKeyboardButton(f"APPROVED {approved} 🔥", callback_data="none"),
                    InlineKeyboardButton(f"DECLINED {declined} ❌", callback_data="none"),
                    InlineKeyboardButton(f"TOTAL CHECKED {checked}", callback_data="none"),
                    InlineKeyboardButton(f"TOTAL {total} ✅", callback_data="none"),
                )
                status_markup.add(InlineKeyboardButton("Close", callback_data="close"))
                try:
                    bot.edit_message_reply_markup(
                        status_msg.chat.id,
                        status_msg.message_id,
                        reply_markup=status_markup
                    )
                except Exception:
                    pass
            except Exception:
                declined += 1
                checked += 1
        # Final panel (same as above)
        status_markup = InlineKeyboardMarkup(row_width=2)
        status_markup.add(
            InlineKeyboardButton(f"APPROVED {approved} 🔥", callback_data="none"),
            InlineKeyboardButton(f"DECLINED {declined} ❌", callback_data="none"),
            InlineKeyboardButton(f"TOTAL CHECKED {checked}", callback_data="none"),
            InlineKeyboardButton(f"TOTAL {total} ✅", callback_data="none"),
        )
        status_markup.add(InlineKeyboardButton("Close", callback_data="close"))
        try:
            bot.edit_message_reply_markup(
                status_msg.chat.id,
                status_msg.message_id,
                reply_markup=status_markup
            )
        except Exception:
            pass

    threading.Thread(target=txt_check).start()
