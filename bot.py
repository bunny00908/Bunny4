import telebot
import config  # This should load your token from .env

from ui import setup_ui_handlers
import chk

bot = telebot.TeleBot(config.BOT_TOKEN)

# Set up your UI/menu handlers
AUTHORIZED_USERS = {}
def save_auth(data): pass
def is_authorized(user_id): return True
setup_ui_handlers(bot, AUTHORIZED_USERS, save_auth, is_authorized)

# Register command handlers
@bot.message_handler(commands=['chk'])
def handle_chk_command(message):
    chk.handle_chk(bot, message)

@bot.message_handler(commands=['mchk'])
def handle_mchk_command(message):
    chk.handle_mchk(bot, message)

@bot.message_handler(commands=['chktxt'], content_types=['document'])
def handle_chktxt_command(message):
    chk.handle_chktxt(bot, message)

# Add imports and handlers for your other commands (gen, bin, fake, scr, status, etc.) here
# Example:
#import gen
#@bot.message_handler(commands=['gen'])
#def handle_gen_command(message):
#    gen.handle_gen(bot, message)

if __name__ == "__main__":
    print("🐰 Bunny Bot is running...")
    bot.infinity_polling()
